"""
backend/tests/conftest.py
Shared fixtures — SQLite test DB with proper session management.
Key fix: patch app.main.SessionLocal so the startup seed_admin()
uses our SQLite test DB instead of PostgreSQL.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# ── Test DB setup ─────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///./test_learnwise.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash(pw: str) -> str:
    return pwd_ctx.hash(pw[:72])


# ── Session-scoped: tables + users created once ───────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Patch app.core.database.SessionLocal and app.main.SessionLocal to point
    to SQLite, drop+create all tables, and seed admin + test users once.
    """
    from app.core import database
    import app.main as main_module
    from app.core.database import Base

    # Create tables in test SQLite DB
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # Patch both references so seed_admin() runs against SQLite
    with patch.object(database, "SessionLocal", TestingSessionLocal), \
         patch.object(main_module, "SessionLocal", TestingSessionLocal):

        # Run the same seed_admin() logic with our patched session
        from app.models.user import User, UserRole
        db = TestingSessionLocal()
        try:
            # Admin user
            if not db.query(User).filter(User.email == "admin@test.com").first():
                db.add(User(
                    username="testadmin", email="admin@test.com",
                    password_hash=_hash("Admin@1234"),
                    display_name="Test Admin",
                    role=UserRole.admin, is_active=True, native_lang="hi",
                ))
            # Regular learner
            if not db.query(User).filter(User.email == "user@test.com").first():
                db.add(User(
                    username="testlearner", email="user@test.com",
                    password_hash=_hash("Test@1234"),
                    display_name="Test Learner",
                    role=UserRole.user, is_active=True, native_lang="hi",
                ))
            db.commit()
        finally:
            db.close()

    yield

    # Cleanup
    import os
    if os.path.exists("./test_learnwise.db"):
        try:
            os.remove("./test_learnwise.db")
        except Exception:
            pass


# ── Function-scoped: fresh session per test ───────────────────────

@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    """
    TestClient with get_db AND app.core.database.SessionLocal both overridden
    to use SQLite. This ensures startup seeding AND request handlers all use
    the same test DB.
    """
    from app.core import database
    import app.main as main_module
    from app.core.database import get_db

    def override_get_db():
        yield db

    with patch.object(database, "SessionLocal", lambda: db), \
         patch.object(main_module, "SessionLocal", lambda: db):
        from app.main import app
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c
        app.dependency_overrides.clear()


# ── User query fixtures ───────────────────────────────────────────

@pytest.fixture()
def regular_user(db):
    from app.models.user import User
    return db.query(User).filter(User.email == "user@test.com").first()


@pytest.fixture()
def admin_user(db):
    from app.models.user import User
    return db.query(User).filter(User.email == "admin@test.com").first()


# ── Token fixtures ────────────────────────────────────────────────

@pytest.fixture()
def user_token(client):
    resp = client.post("/api/auth/login", json={"email": "user@test.com", "password": "Test@1234"})
    assert resp.status_code == 200, f"User login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture()
def admin_token(client):
    # Admin users must use the dedicated admin login endpoint
    resp = client.post("/api/auth/admin/login", json={"email": "admin@test.com", "password": "Admin@1234"})
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
