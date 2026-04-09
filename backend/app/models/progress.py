"""
backend/app/models/progress.py
ORM models for tracking user learning progress:
  - UserLanguageProgress: per language-pair progress (XP, current position by month/block/activity)
  - ActivityCompletion: individual activity attempt records with string activityId + AI feedback

Schema v2: current_week → current_block, activity_id → String (matches data_README activityId format)
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserLanguageProgress(Base):
    __tablename__ = "user_language_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lang_pair_id = Column(String(10), nullable=False)   # e.g. "hi-ja"
    total_xp = Column(Integer, default=0)
    current_month = Column(Integer, default=1)
    current_block = Column(Integer, default=1)           # was current_week
    current_activity_id = Column(Integer, default=1)    # global sequential int (1-144)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="language_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "lang_pair_id", name="uq_user_lang_pair"),
    )

    def __repr__(self):
        return f"<Progress user={self.user_id} pair={self.lang_pair_id} m={self.current_month} b={self.current_block} a={self.current_activity_id}>"


class ActivityCompletion(Base):
    __tablename__ = "activity_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lang_pair_id = Column(String(10), nullable=False)
    # Sequential integer ID (1-144) — used for unlock ordering
    activity_seq_id = Column(Integer, nullable=False, default=1)
    # String activityId from JSON (e.g. "ja_hi_M1B1_lesson_1") — for detailed tracking
    activity_json_id = Column(String(80), nullable=True)
    activity_type = Column(String(20), nullable=False)   # lesson|pronunciation|reading|writing|listening|vocabulary|speaking|test
    month_number = Column(Integer, nullable=True)
    block_number = Column(Integer, nullable=True)
    score_earned = Column(Integer, default=0)
    max_score = Column(Integer, nullable=False)
    passed = Column(Boolean, default=False)
    attempts = Column(Integer, default=1)
    ai_feedback = Column(Text, nullable=True)
    ai_suggestion = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_completions")

    __table_args__ = (
        UniqueConstraint("user_id", "lang_pair_id", "activity_seq_id", name="uq_user_activity_completion"),
    )

    def __repr__(self):
        return f"<Completion seqId={self.activity_seq_id} jsonId={self.activity_json_id} score={self.score_earned}/{self.max_score}>"
