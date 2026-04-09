"""
backend/app/schemas/admin.py
Pydantic schemas for admin-only endpoints.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID


class AdminUserOut(BaseModel):
    id: UUID
    username: str
    email: str
    display_name: Optional[str]
    role: str
    is_active: bool
    native_lang: Optional[str]
    created_at: datetime
    last_active: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UpdateUserRoleRequest(BaseModel):
    role: str   # "user" | "admin"


class PlatformStats(BaseModel):
    total_users: int
    active_today: int
    total_completions: int
    total_xp_awarded: int
    language_pairs: int
    top_language_pair: Optional[str]


class CreateLanguagePairRequest(BaseModel):
    source_lang_id: str       # e.g. "hi"
    source_lang_name: str     # e.g. "Hindi"
    source_lang_flag: str     # e.g. "🇮🇳"
    target_lang_id: str       # e.g. "fr"
    target_lang_name: str     # e.g. "French"
    target_lang_flag: str     # e.g. "🇫🇷"


class UpdateContentRequest(BaseModel):
    file_path: str            # relative path e.g. "month-1/week-1-lesson.json"
    content: Dict[str, Any]  # full JSON content to write


class AdminActivityUpdate(BaseModel):
    activity_id: int
    new_label: Optional[str] = None
    new_xp: Optional[int] = None
    new_type: Optional[str] = None


class ContentFileInfo(BaseModel):
    path: str
    size_bytes: int
    activity_type: Optional[str]
    week: Optional[int]
    month: Optional[int]
