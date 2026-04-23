"""
backend/app/main.py
FastAPI application entry point for LearnWise backend.
- Registers all routers under /api prefix
- Configures CORS for React frontend
- Creates DB tables + seeds admin user on startup
- Serves uploaded audio files as static files
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.database import create_tables, SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_admin():
    """Create the default admin account if it doesn't exist."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not existing:
            admin = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                display_name="LearnWise Admin",
                role=UserRole.admin,
                native_lang="en",
            )
            db.add(admin)
            db.commit()
            logger.info(f"Admin user created: {settings.ADMIN_EMAIL}")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Failed to seed admin: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown lifecycle handler."""
    logger.info("LearnWise backend starting up...")
    create_tables()
    seed_admin()
    # Ensure uploads directory exists
    uploads_dir = Path(settings.data_path).parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Startup complete. Server ready.")
    yield
    logger.info("LearnWise backend shutting down.")


app = FastAPI(
    title="LearnWise API",
    description="AI-powered language learning platform backend",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for uploaded audio and curriculum assets ──
uploads_path = str(Path(settings.data_path).parent / "uploads")
languages_path = str(Path(settings.data_path) / "languages")
os.makedirs(uploads_path, exist_ok=True)
os.makedirs(languages_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
app.mount("/static", StaticFiles(directory=languages_path), name="static")

# ── Register routers ──────────────────────────────────────────
from app.routers import auth, content, progress, validate, speech, leaderboard, friends, admin, users

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(validate.router, prefix="/api")
app.include_router(speech.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "2.0.0"}
