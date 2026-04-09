"""
backend/app/schemas/progress.py
Pydantic schemas for progress tracking and activity completions.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ProgressOut(BaseModel):
    id: UUID
    user_id: UUID
    lang_pair_id: str
    total_xp: int
    current_month: int
    current_week: int
    current_activity_id: int
    started_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StartProgressRequest(BaseModel):
    lang_pair_id: str


class CompleteActivityRequest(BaseModel):
    activity_id: int
    activity_type: str
    lang_pair_id: str
    score_earned: int
    max_score: int
    passed: bool
    ai_feedback: Optional[str] = None
    ai_suggestion: Optional[str] = None


class CompletionOut(BaseModel):
    id: UUID
    activity_id: int
    activity_type: str
    score_earned: int
    max_score: int
    passed: bool
    attempts: int
    ai_feedback: Optional[str]
    ai_suggestion: Optional[str]
    completed_at: datetime

    model_config = {"from_attributes": True}


class UserProgressSummary(BaseModel):
    lang_pair_id: str
    total_xp: int
    current_month: int
    current_week: int
    current_activity_id: int
    completed_activities: List[CompletionOut]


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    total_xp: int
