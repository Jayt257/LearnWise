"""
backend/app/schemas/user.py
Pydantic schemas for user profile endpoints.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserProfileOut(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    native_lang: Optional[str]
    role: str
    created_at: datetime
    last_active: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserPublicOut(BaseModel):
    """Reduced profile for public search results / friend cards."""
    id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    native_lang: Optional[str]

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    native_lang: Optional[str] = None


class UserSearchResult(BaseModel):
    users: List[UserPublicOut]
    total: int


class FriendRequestOut(BaseModel):
    id: UUID
    sender: UserPublicOut
    receiver: UserPublicOut
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
