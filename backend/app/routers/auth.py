"""
backend/app/routers/auth.py
Authentication endpoints:
  POST /api/auth/register   - Create new user account
  POST /api/auth/login      - Login and receive JWT
  POST /api/auth/admin/login - Admin-only login
  GET  /api/auth/me         - Get current user info
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, AdminLoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_to_out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        native_lang=user.native_lang,
        role=user.role.value,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check uniqueness
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.display_name or req.username,
        native_lang=req.native_lang or "en",
        role=UserRole.user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=_user_to_out(user))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email + password."""
    user = db.query(User).filter(User.email == req.email, User.role == UserRole.user).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user.last_active = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=_user_to_out(user))


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin-only login endpoint."""
    user = db.query(User).filter(User.email == req.email, User.role == UserRole.admin).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=_user_to_out(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user."""
    return _user_to_out(current_user)
