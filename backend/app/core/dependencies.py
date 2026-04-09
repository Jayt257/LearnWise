"""
backend/app/core/dependencies.py
Reusable FastAPI dependency functions:
  - get_current_user: extracts + validates JWT, returns User model
  - require_admin:    same as above but also checks role == 'admin'
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .security import decode_token
from app.models.user import User, UserRole

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise exc
    payload = decode_token(credentials.credentials)
    if not payload:
        raise exc
    user_id: str = payload.get("sub")
    if not user_id:
        raise exc
    
    import uuid
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise exc
        
    user = db.query(User).filter(User.id == user_uuid, User.is_active == True).first()
    if not user:
        raise exc
    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
