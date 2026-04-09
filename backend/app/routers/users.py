"""
backend/app/routers/users.py
User profile and search endpoints.
  GET  /api/users/me        - Current user's full profile
  PUT  /api/users/me        - Update profile
  GET  /api/users/search    - Search users by username
  GET  /api/users/{user_id} - Public profile of another user
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.progress import UserLanguageProgress
from app.schemas.user import UserProfileOut, UserPublicOut, UpdateProfileRequest, UserSearchResult

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileOut)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return UserProfileOut.model_validate(current_user)


@router.put("/me", response_model=UserProfileOut)
def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.display_name is not None:
        current_user.display_name = req.display_name
    if req.avatar_url is not None:
        current_user.avatar_url = req.avatar_url
    if req.native_lang is not None:
        current_user.native_lang = req.native_lang
    db.commit()
    db.refresh(current_user)
    return UserProfileOut.model_validate(current_user)


@router.get("/search", response_model=UserSearchResult)
def search_users(
    q: str = Query(..., min_length=1, description="Username prefix to search"),
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search users by username (case-insensitive prefix match)."""
    users = db.query(User).filter(
        User.username.ilike(f"%{q}%"),
        User.id != current_user.id,
        User.is_active == True,
    ).limit(limit).all()

    return UserSearchResult(
        users=[UserPublicOut.model_validate(u) for u in users],
        total=len(users),
    )


@router.get("/{user_id}", response_model=UserPublicOut)
def get_user_profile(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get public profile of any user."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublicOut.model_validate(user)


@router.get("/{user_id}/progress")
def get_user_progress_public(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get public progress summary for viewing a friend's progress."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress_records = db.query(UserLanguageProgress).filter(
        UserLanguageProgress.user_id == user_id
    ).all()

    return {
        "user": UserPublicOut.model_validate(user),
        "progress": [
            {
                "lang_pair_id": p.lang_pair_id,
                "total_xp": p.total_xp,
                "current_month": p.current_month,
                "current_week": p.current_week,
            }
            for p in progress_records
        ]
    }
