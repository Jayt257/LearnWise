"""
backend/app/routers/progress.py
User progress tracking endpoints (block-based schema v2).
  GET  /api/progress                       - All progress for current user
  GET  /api/progress/{pair_id}             - Progress for specific pair
  POST /api/progress/{pair_id}/start       - Start a new language pair
  POST /api/progress/{pair_id}/complete    - Record activity completion & update XP
  GET  /api/progress/{pair_id}/completions - Get completed activities list
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.progress import UserLanguageProgress, ActivityCompletion
from app.schemas.progress import (
    ProgressOut, StartProgressRequest, CompleteActivityRequest,
    CompletionOut, UserProgressSummary
)

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("", response_model=List[ProgressOut])
def get_all_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all language pair progress for the current user."""
    records = db.query(UserLanguageProgress).filter(
        UserLanguageProgress.user_id == current_user.id
    ).all()
    return [ProgressOut.model_validate(r) for r in records]


@router.get("/{pair_id}", response_model=ProgressOut)
def get_pair_progress(
    pair_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get progress for a specific language pair."""
    record = db.query(UserLanguageProgress).filter(
        and_(
            UserLanguageProgress.user_id == current_user.id,
            UserLanguageProgress.lang_pair_id == pair_id,
        )
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Progress not found. Start this language pair first.")
    return ProgressOut.model_validate(record)


@router.post("/{pair_id}/start", response_model=ProgressOut, status_code=201)
def start_pair(
    pair_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new language learning path."""
    existing = db.query(UserLanguageProgress).filter(
        and_(
            UserLanguageProgress.user_id == current_user.id,
            UserLanguageProgress.lang_pair_id == pair_id,
        )
    ).first()
    if existing:
        return ProgressOut.model_validate(existing)

    record = UserLanguageProgress(
        user_id=current_user.id,
        lang_pair_id=pair_id,
        total_xp=0,
        current_month=1,
        current_block=1,
        current_activity_id=1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ProgressOut.model_validate(record)


def _derive_month_block(activity_seq_id: int) -> tuple[int, int]:
    """
    Derive (month, block) from a global sequential activity ID (1-144).
    - 8 activities per block, 6 blocks per month = 48 per month
    - month 1 → IDs 1-48, month 2 → IDs 49-96, month 3 → IDs 97-144
    """
    if activity_seq_id < 1:
        activity_seq_id = 1
    zero_based = activity_seq_id - 1
    month = (zero_based // 48) + 1
    block = ((zero_based % 48) // 8) + 1
    return month, block


@router.post("/{pair_id}/complete", response_model=CompletionOut)
def complete_activity(
    pair_id: str,
    req: CompleteActivityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record an activity completion and update user XP.
    - SCORE_THRESHOLD_OVERRIDE > 0: enforce a minimum raw score to count as passed.
    - SCORE_THRESHOLD_OVERRIDE = -1 (default): use the passed flag from the validate endpoint.
    - If user already completed this activity, updates if new score is better.
    - Only adds XP for the improvement over the previous best score.
    - Advances position when activity passed and it's exactly the current one.
    """
    # Apply global score threshold override only when explicitly set to a positive value
    effective_passed = req.passed
    if settings.SCORE_THRESHOLD_OVERRIDE > 0:
        # Positive override: require minimum raw score
        effective_passed = req.score_earned >= settings.SCORE_THRESHOLD_OVERRIDE

    # Derive month/block from seq ID if not provided
    month_num = req.month_number
    block_num = req.block_number
    if month_num is None or block_num is None:
        month_num, block_num = _derive_month_block(req.activity_seq_id)

    # Find or create progress record
    progress = db.query(UserLanguageProgress).filter(
        and_(
            UserLanguageProgress.user_id == current_user.id,
            UserLanguageProgress.lang_pair_id == pair_id,
        )
    ).first()
    if not progress:
        progress = UserLanguageProgress(
            user_id=current_user.id,
            lang_pair_id=pair_id,
            total_xp=0,
            current_month=1,
            current_block=1,
            current_activity_id=req.activity_seq_id,
        )
        db.add(progress)

    # Find existing completion for this activity
    existing = db.query(ActivityCompletion).filter(
        and_(
            ActivityCompletion.user_id == current_user.id,
            ActivityCompletion.lang_pair_id == pair_id,
            ActivityCompletion.activity_seq_id == req.activity_seq_id,
        )
    ).first()

    xp_delta = 0
    if existing:
        # Only award XP for score improvement
        if req.score_earned > existing.score_earned:
            xp_delta = req.score_earned - existing.score_earned
            existing.score_earned = req.score_earned
            existing.passed = effective_passed
        existing.attempts += 1
        existing.ai_feedback = req.ai_feedback
        existing.ai_suggestion = req.ai_suggestion
        existing.completed_at = datetime.utcnow()
        if req.activity_json_id:
            existing.activity_json_id = req.activity_json_id
        completion = existing
    else:
        # First attempt
        xp_delta = req.score_earned
        completion = ActivityCompletion(
            user_id=current_user.id,
            lang_pair_id=pair_id,
            activity_seq_id=req.activity_seq_id,
            activity_json_id=req.activity_json_id,
            activity_type=req.activity_type,
            month_number=month_num,
            block_number=block_num,
            score_earned=req.score_earned,
            max_score=req.max_score,
            passed=effective_passed,
            attempts=1,
            ai_feedback=req.ai_feedback,
            ai_suggestion=req.ai_suggestion,
        )
        db.add(completion)

    # Update total XP
    progress.total_xp += xp_delta
    progress.last_activity_at = datetime.utcnow()

    # Advance position if activity passed and it is exactly the current one
    if effective_passed and req.activity_seq_id == progress.current_activity_id:
        next_id = progress.current_activity_id + 1
        progress.current_activity_id = next_id
        # Update current_month and current_block from advanced position
        progress.current_month, progress.current_block = _derive_month_block(next_id)

    db.commit()
    db.refresh(completion)
    return CompletionOut.model_validate(completion)


@router.get("/{pair_id}/completions", response_model=List[CompletionOut])
def get_completions(
    pair_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all activity completions for a language pair."""
    completions = db.query(ActivityCompletion).filter(
        and_(
            ActivityCompletion.user_id == current_user.id,
            ActivityCompletion.lang_pair_id == pair_id,
        )
    ).all()
    return [CompletionOut.model_validate(c) for c in completions]
