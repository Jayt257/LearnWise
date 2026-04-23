"""
backend/app/core/database.py
SQLAlchemy engine + session factory + Base for all ORM models.
Creates all tables on startup via Base.metadata.create_all().
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# SQLite doesn't support pool_size / max_overflow — only add these for Postgres
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_engine_kwargs = {"pool_pre_ping": True}
if not _is_sqlite:
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20
else:
    from sqlalchemy.pool import StaticPool
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session, closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Called at app startup to create all tables if they don't exist."""
    from app.models import user, progress, friends  # noqa: F401 — import to register models
    Base.metadata.create_all(bind=engine)
