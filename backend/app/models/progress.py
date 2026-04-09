"""
backend/app/models/progress.py
ORM models for tracking user learning progress:
  - UserLanguageProgress: per language-pair progress (XP, current position)
  - ActivityCompletion: individual activity attempt records with AI feedback
"""

import uuid
import enum
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
    lang_pair_id = Column(String(10), nullable=False)   # e.g. "hi-en"
    total_xp = Column(Integer, default=0)
    current_month = Column(Integer, default=1)
    current_week = Column(Integer, default=1)
    current_activity_id = Column(Integer, default=1)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="language_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "lang_pair_id", name="uq_user_lang_pair"),
    )

    def __repr__(self):
        return f"<Progress user={self.user_id} pair={self.lang_pair_id} xp={self.total_xp}>"


class ActivityCompletion(Base):
    __tablename__ = "activity_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lang_pair_id = Column(String(10), nullable=False)
    activity_id = Column(Integer, nullable=False)
    activity_type = Column(String(20), nullable=False)   # lesson | vocab | reading | etc.
    score_earned = Column(Integer, default=0)
    max_score = Column(Integer, nullable=False)
    passed = Column(Boolean, default=False)
    attempts = Column(Integer, default=1)
    ai_feedback = Column(Text, nullable=True)
    ai_suggestion = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_completions")

    def __repr__(self):
        return f"<Completion activity={self.activity_id} score={self.score_earned}/{self.max_score}>"
