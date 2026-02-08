from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.database.models.accounts import ActivationTokenModel, RefreshTokenModel, UserGroupEnum, UserGroupModel, UserModel
from src.security.jwt import JWTManager
from src.security.passwords import PasswordManager
from src.services.mailer import MailerInterface, OutgoingEmail


class AccountsService:
    def __init__(self, db: Session, mailer: MailerInterface) -> None:
        self.db = db
        self.mailer = mailer
        self.jwt = JWTManager(settings.app_secret_key)

    def _get_user_group(self, group: UserGroupEnum) -> UserGroupModel:
        q = select(UserGroupModel).where(UserGroupModel.name == group)
        obj = self.db.scalar(q)
        if obj is None:
            obj = UserGroupModel(name=group)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def register(self, email: str, password: str) -> None:
        PasswordManager.validate(password)

        exists = self.db.scalar(select(UserModel).where(UserModel.email == email))
        if exists is not None:
            raise ValueError("Email already registered.")

        group = self._get_user_group(UserGroupEnum.USER)
        user = UserModel(
            email=email,
            hashed_password=PasswordManager.hash(password),
            is_active=False,
            group_id=group.id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        self._issue_activation(user)

    def _issue_activation(self, user: UserModel) -> None:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        # replace existing token
        if user.activation_token is not None:
            self.db.delete(user.activation_token)
            self.db.commit()

        act = ActivationTokenModel(user_id=user.id, token=token, expires_at=expires_at)
        self.db.add(act)
        self.db.commit()

        self.mailer.send(
            OutgoingEmail(
                to=user.email,
                subject="Activate your account",
                body=f"Use this token to activate: {token}",
            )
        )

    def activate(self, token: str) -> None:
        act = self.db.scalar(select(ActivationTokenModel).where(ActivationTokenModel.token == token))
        if act is None:
            raise ValueError("Invalid token.")

        if act.expires_at <= datetime.now(timezone.utc):
            raise ValueError("Token expired.")

        user = self.db.get(UserModel, act.user_id)
        if user is None:
            raise ValueError("User not found.")

        user.is_active = True
        self.db.delete(act)
        self.db.commit()

    def resend_activation(self, email: str) -> None:
        user = self.db.scalar(select(UserModel).where(UserModel.email == email))
        if user is None:
            # не палимо існування емейлу
            return
        if user.is_active:
            return
        self._issue_activation(user)

    def login(self, email: str, password: str) -> tuple[str, str]:
        user = self.db.scalar(select(UserModel).where(UserModel.email == email))
        if user is None or not PasswordManager.verify(password, user.hashed_password):
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise ValueError("Account is not activated.")

        access = self.jwt.encode({"sub": str(user.id), "type": "access"}, timedelta(minutes=settings.access_token_ttl_min))
        refresh_token = secrets.token_urlsafe(32)
        refresh_jwt = self.jwt.encode(
            {"sub": str(user.id), "type": "refresh", "rt": refresh_token},
            timedelta(days=settings.refresh_token_ttl_days),
        )

        # store refresh token so we can revoke it
        rt = RefreshTokenModel(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days),
        )
        self.db.add(rt)
        self.db.commit()

        return access, refresh_jwt

    def refresh_access(self, refresh_jwt: str) -> str:
        payload = self.jwt.decode(refresh_jwt)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type.")

        user_id = int(payload["sub"])
        token_marker = str(payload["rt"])

        stored = self.db.scalar(select(RefreshTokenModel).where(RefreshTokenModel.token == token_marker))
        if stored is None or stored.user_id != user_id:
            raise ValueError("Refresh token revoked.")

        if stored.expires_at <= datetime.now(timezone.utc):
            raise ValueError("Refresh token expired.")

        return self.jwt.encode({"sub": str(user_id), "type": "access"}, timedelta(minutes=settings.access_token_ttl_min))

    def logout(self, refresh_jwt: str) -> None:
        payload = self.jwt.decode(refresh_jwt)
        if payload.get("type") != "refresh":
            return
        token_marker = str(payload.get("rt"))
        stored = self.db.scalar(select(RefreshTokenModel).where(RefreshTokenModel.token == token_marker))
        if stored is not None:
            self.db.delete(stored)
            self.db.commit()
