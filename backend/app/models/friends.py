"""
backend/app/models/friends.py
ORM model for friend requests between users.
Status transitions: pending → accepted | declined
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class FriendRequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(FriendRequestStatus), default=FriendRequestStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_requests")

    __table_args__ = (
        UniqueConstraint("sender_id", "receiver_id", name="uq_friend_pair"),
    )

    def __repr__(self):
        return f"<FriendRequest {self.sender_id} → {self.receiver_id} [{self.status}]>"
