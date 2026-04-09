"""
backend/app/models/__init__.py
Import all ORM models here so SQLAlchemy registers them with Base.metadata.
"""
from .user import User, UserRole  # noqa
from .progress import UserLanguageProgress, ActivityCompletion  # noqa
from .friends import FriendRequest, FriendRequestStatus  # noqa
