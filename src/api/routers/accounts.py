from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.accounts import (
    ActivateRequestSchema,
    MessageResponseSchema,
    RefreshRequestSchema,
    ResendActivationRequestSchema,
    TokenPairSchema,
    UserLoginRequestSchema,
    UserRegistrationRequestSchema,
)
from src.services.accounts import AccountsService
from src.services.mailer import DevConsoleMailer

router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


def get_accounts_service(db: Session = Depends(get_db)) -> AccountsService:
    return AccountsService(db=db, mailer=DevConsoleMailer())


@router.post("/register", response_model=MessageResponseSchema, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegistrationRequestSchema, svc: AccountsService = Depends(get_accounts_service)) -> MessageResponseSchema:
    try:
        svc.register(email=str(payload.email), password=payload.password)
        return MessageResponseSchema(message="Registration successful. Check email for activation.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/activate", response_model=MessageResponseSchema)
def activate(payload: ActivateRequestSchema, svc: AccountsService = Depends(get_accounts_service)) -> MessageResponseSchema:
    try:
        svc.activate(token=payload.token)
        return MessageResponseSchema(message="Account activated.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-activation", response_model=MessageResponseSchema)
def resend(payload: ResendActivationRequestSchema, svc: AccountsService = Depends(get_accounts_service)) -> MessageResponseSchema:
    svc.resend_activation(email=str(payload.email))
    return MessageResponseSchema(message="If the email exists, a new activation token was sent.")


@router.post("/login", response_model=TokenPairSchema)
def login(payload: UserLoginRequestSchema, svc: AccountsService = Depends(get_accounts_service)) -> TokenPairSchema:
    try:
        access, refresh = svc.login(email=str(payload.email), password=payload.password)
        return TokenPairSchema(access=access, refresh=refresh)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh", response_model=TokenPairSchema)
def refresh(payload: RefreshRequestSchema, svc: AccountsService = Depends(get_accounts_service)) -> TokenPairSchema:
    try:
        new_access = svc.refresh_access(refresh_jwt=payload.refresh)
        return TokenPairSchema(access=new_access, refresh=payload.refresh)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout", response_model=MessageResponseSchema)
def logout(payload: RefreshRequestSchema, svc: AccountsService = Depends(get_accounts_service)) -> MessageResponseSchema:
    svc.logout(refresh_jwt=payload.refresh)
    return MessageResponseSchema(message="Logged out.")
