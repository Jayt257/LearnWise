import pytest
from app.core.database import get_db, create_tables
from app.core.dependencies import get_current_user, get_current_active_user, require_admin
from app.core.security import create_access_token
from app.models.user import User, UserRole
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import uuid

def test_get_db_coverage():
    """Test the raw get_db generator (usually overridden in integration tests)"""
    gen = get_db()
    db = next(gen)
    assert db is not None
    try:
        next(gen)
    except StopIteration:
        pass


def test_sqlite_engine_init(monkeypatch):
    """Test that sqlite init works"""
    import importlib
    import app.core.config as py_config
    monkeypatch.setattr(py_config.settings, "DATABASE_URL", "sqlite:///:memory:")
    import app.core.database as py_db
    importlib.reload(py_db)
    assert py_db._is_sqlite is True
    monkeypatch.undo()
    importlib.reload(py_db)


def test_dependencies(db):
    """Cover the exception branches in dependencies.py"""
    # 1. No credentials
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=None, db=db)
    assert excinfo.value.status_code == 401

    # 2. Token without sub
    bad_token = create_access_token({})
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=bad_token)
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=creds, db=db)
    assert excinfo.value.status_code == 401

    # 3. Invalid UUID sub
    bad_token2 = create_access_token({"sub": "not-a-uuid"})
    creds2 = HTTPAuthorizationCredentials(scheme="Bearer", credentials=bad_token2)
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=creds2, db=db)
    assert excinfo.value.status_code == 401

    # 4. Valid UUID but user not in DB
    ghost_user_id = str(uuid.uuid4())
    bad_token3 = create_access_token({"sub": ghost_user_id})
    creds3 = HTTPAuthorizationCredentials(scheme="Bearer", credentials=bad_token3)
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=creds3, db=db)
    assert excinfo.value.status_code == 401

    # 5. get_current_active_user
    # Create inactive user
    u = User(username="inactive_dep", email="inactive_dep@test.com", password_hash="hash", role=UserRole.user, is_active=False)
    db.add(u)
    db.commit()
    db.refresh(u)
    with pytest.raises(HTTPException) as excinfo:
        get_current_active_user(user=u)
    assert excinfo.value.status_code == 400
    
    # Active user
    u.is_active = True
    db.commit()
    good_token = create_access_token({"sub": str(u.id)})
    creds_good = HTTPAuthorizationCredentials(scheme="Bearer", credentials=good_token)
    assert get_current_user(credentials=creds_good, db=db) == u

    assert get_current_active_user(user=u) == u

    # 6. Invalid token format causing decode_token to return None
    bad_token4 = "completely.invalid.token"
    creds4 = HTTPAuthorizationCredentials(scheme="Bearer", credentials=bad_token4)
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(credentials=creds4, db=db)
    assert excinfo.value.status_code == 401

    # 7. require_admin with non-admin user
    u2 = User(username="admin_dep", email="admin_dep@test.com", password_hash="hash", role=UserRole.user, is_active=True)
    db.add(u2)
    db.commit()
    db.refresh(u2)
    with pytest.raises(HTTPException) as excinfo:
        require_admin(user=u2)
    assert excinfo.value.status_code == 403

    # Admin user
    u2.role = UserRole.admin
    assert require_admin(user=u2) == u2

def test_security_functions():
    from app.core.security import hash_password, verify_password, create_access_token, decode_token
    h = hash_password("testpass")
    assert verify_password("testpass", h) is True
    assert verify_password("wrong", h) is False
    
    t = create_access_token({"sub": "123"})
    d = decode_token(t)
    assert d["sub"] == "123"
    
    # decode_token exception returns None
    assert decode_token("invalid.token") is None

def test_database_create_tables():
    from app.core.database import create_tables
    # Just call it; it uses create_all with checkfirst=True
    create_tables()
