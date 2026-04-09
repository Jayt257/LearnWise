"""
backend/app/routers/leaderboard.py
Leaderboard endpoints — ranked by XP per language pair.
  GET /api/leaderboard/{pair_id}         - Global leaderboard
  GET /api/leaderboard/{pair_id}/friends - Friends-only leaderboard
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.progress import UserLanguageProgress
from app.models.friends import FriendRequest, FriendRequestStatus
from app.schemas.progress import LeaderboardEntry

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/{pair_id}", response_model=List[LeaderboardEntry])
def get_leaderboard(
    pair_id: str,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Global leaderboard for a language pair, sorted by XP descending."""
    records = (
        db.query(UserLanguageProgress, User)
        .join(User, User.id == UserLanguageProgress.user_id)
        .filter(
            UserLanguageProgress.lang_pair_id == pair_id,
            User.is_active == True,
        )
        .order_by(UserLanguageProgress.total_xp.desc())
        .limit(limit)
        .all()
    )

    return [
        LeaderboardEntry(
            rank=i + 1,
            user_id=str(u.id),
            username=u.username,
            display_name=u.display_name,
            avatar_url=u.avatar_url,
            total_xp=p.total_xp,
        )
        for i, (p, u) in enumerate(records)
    ]


@router.get("/{pair_id}/friends", response_model=List[LeaderboardEntry])
def get_friends_leaderboard(
    pair_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Leaderboard including only the current user + accepted friends."""
    # Find friend IDs
    accepted = db.query(FriendRequest).filter(
        and_(
            FriendRequest.status == FriendRequestStatus.accepted,
            or_(
                FriendRequest.sender_id == current_user.id,
                FriendRequest.receiver_id == current_user.id,
            )
        )
    ).all()

    # or_ imported at top-level
    friend_ids = set()
    for req in accepted:
        if str(req.sender_id) == str(current_user.id):
            friend_ids.add(req.receiver_id)
        else:
            friend_ids.add(req.sender_id)
    friend_ids.add(current_user.id)

    records = (
        db.query(UserLanguageProgress, User)
        .join(User, User.id == UserLanguageProgress.user_id)
        .filter(
            UserLanguageProgress.lang_pair_id == pair_id,
            UserLanguageProgress.user_id.in_(friend_ids),
            User.is_active == True,
        )
        .order_by(UserLanguageProgress.total_xp.desc())
        .all()
    )

    return [
        LeaderboardEntry(
            rank=i + 1,
            user_id=str(u.id),
            username=u.username,
            display_name=u.display_name,
            avatar_url=u.avatar_url,
            total_xp=p.total_xp,
        )
        for i, (p, u) in enumerate(records)
    ]
