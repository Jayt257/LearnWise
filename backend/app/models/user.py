"""
backend/app/models/user.py
SQLAlchemy ORM model for users table.
Stores credentials, profile info, and role (user | admin).
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    native_lang = Column(String(5), nullable=True, default="en")
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    language_progress = relationship(
        "UserLanguageProgress", back_populates="user", cascade="all, delete-orphan"
    )
    activity_completions = relationship(
        "ActivityCompletion", back_populates="user", cascade="all, delete-orphan"
    )
    sent_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
