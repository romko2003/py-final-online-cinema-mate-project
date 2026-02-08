from pydantic import BaseModel, EmailStr, Field


class MessageResponseSchema(BaseModel):
    message: str


class UserRegistrationRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class TokenPairSchema(BaseModel):
    access: str
    refresh: str


class RefreshRequestSchema(BaseModel):
    refresh: str


class ActivateRequestSchema(BaseModel):
    token: str


class ResendActivationRequestSchema(BaseModel):
    email: EmailStr
