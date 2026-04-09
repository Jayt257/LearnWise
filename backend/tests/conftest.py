"""
backend/tests/conftest.py
Pytest configuration and shared fixtures for LearnWise backend tests.
Uses SQLite in-memory database — database.py handles SQLite-safe engine creation.
"""

import os
import pytest

# ── Set ALL env vars BEFORE any app module is imported ────────
# Must use os.environ directly (not setdefault) because pydantic-settings
# reads these at import time from the environment.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["GROQ_API_KEY"] = "test-groq-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["ADMIN_EMAIL"] = "admin@learnwise.app"
os.environ["ADMIN_PASSWORD"] = "Admin@LearnWise2026"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["DATA_DIR"] = "data"
os.environ["WHISPER_MODEL"] = "base"
os.environ["GROQ_MODEL"] = "llama3-8b-8192"

# ── Import app after env vars are set ─────────────────────────
from app.core.database import Base, get_db, engine, SessionLocal  # noqa
from app.main import app  # noqa
from fastapi.testclient import TestClient  # noqa


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all tables once for the entire test session."""
    from app.models import user, progress, friends  # noqa — register models
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a DB session. Each test gets a fresh session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with DB dependency overridden to the test session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper factories ───────────────────────────────────────────

def register_user(client, username="testuser", email="test@example.com",
                  password="TestPass123!", display_name="Test User"):
    """Register a test user and return the full response object."""
    return client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "display_name": display_name,
        "native_lang": "en",
    })


def get_auth_headers(client, username="testuser", email="test@example.com",
                     password="TestPass123!"):
    """Register (if needed) + login, return Bearer auth headers dict."""
    register_user(client, username, email, password)
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    token = res.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def _seed_admin(db):
    """Insert admin user into test DB if not already present."""
    from app.core.security import hash_password
    from app.models.user import User, UserRole
    existing = db.query(User).filter(User.email == "admin@learnwise.app").first()
    if not existing:
        admin = User(
            username="admin",
            email="admin@learnwise.app",
            password_hash=hash_password("Admin@LearnWise2026"),
            display_name="Admin",
            native_lang="en",
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()


def get_admin_headers(client, db):
    """Seed admin and return Bearer admin auth headers."""
    _seed_admin(db)
    res = client.post("/api/auth/admin/login", json={
        "email": "admin@learnwise.app",
        "password": "Admin@LearnWise2026",
    })
    token = res.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(client):
    import uuid as _uuid
    uid = _uuid.uuid4().hex[:8]
    return get_auth_headers(client, f"u{uid}", f"u{uid}@example.com", "TestPass123!")


@pytest.fixture()
def admin_headers(client, db):
    return get_admin_headers(client, db)


