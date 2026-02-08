from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class UserGroupEnum(str, enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class GenderEnum(str, enum.Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"


class UserGroupModel(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[UserGroupEnum] = mapped_column(Enum(UserGroupEnum), unique=True, nullable=False)

    users: Mapped[list["UserModel"]] = relationship(back_populates="group")


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("user_groups.id"), nullable=False)

    group: Mapped["UserGroupModel"] = relationship(back_populates="users")
    profile: Mapped["UserProfileModel | None"] = relationship(back_populates="user", uselist=False)
    activation_token: Mapped["ActivationTokenModel | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(10), nullable=True)
    info: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="profile")


class ActivationTokenModel(Base):
    __tablename__ = "activation_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="activation_token")


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (UniqueConstraint("user_id", "token", name="uq_user_refresh_token"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="refresh_tokens")
