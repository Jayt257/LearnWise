"""
backend/app/schemas/auth.py
Pydantic schemas for authentication endpoints (register, login, token).
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
import re


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    native_lang: Optional[str] = "en"

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be 3-50 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    native_lang: Optional[str]
    role: str

    model_config = {"from_attributes": True}


# Resolve forward ref
TokenResponse.model_rebuild()
