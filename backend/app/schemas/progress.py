"""
backend/app/schemas/progress.py
Pydantic schemas for progress tracking and activity completions.
Schema v2: current_week → current_block, activity_id → int (seq) + string (json)
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
    current_block: int           # was current_week
    current_activity_id: int    # sequential integer position (1-144)
    started_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StartProgressRequest(BaseModel):
    lang_pair_id: str


class CompleteActivityRequest(BaseModel):
    activity_seq_id: int          # sequential integer (1-144) — used for unlock logic
    activity_json_id: Optional[str] = None  # string activityId from JSON e.g. "ja_hi_M1B1_lesson_1"
    activity_type: str
    lang_pair_id: str
    month_number: Optional[int] = None
    block_number: Optional[int] = None
    score_earned: int
    max_score: int
    passed: bool
    ai_feedback: Optional[str] = None
    ai_suggestion: Optional[str] = None


class CompletionOut(BaseModel):
    id: UUID
    activity_seq_id: int
    activity_json_id: Optional[str] = None
    activity_type: str
    month_number: Optional[int] = None
    block_number: Optional[int] = None
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
    current_block: int
    current_activity_id: int
    completed_activities: List[CompletionOut]


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    total_xp: int
