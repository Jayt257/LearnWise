"""
backend/tests/test_auth.py
Auth endpoint tests: register, login, get profile, token validation.
"""
import pytest


def test_register_new_user(client):
    resp = client.post("/api/auth/register", json={
        "username": "newlearner",
        "email": "newlearner@test.com",
        "password": "NewPass@123",
        "native_lang": "hi",
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    # Register returns {access_token, token_type, user}
    assert "user" in data
    assert data["user"]["email"] == "newlearner@test.com"
    assert data["user"]["role"] == "user"


def test_register_duplicate_email(client):
    payload = {"username": "dup1", "email": "dup@test.com", "password": "Pass@123", "native_lang": "hi"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code in (400, 409)


def test_login_success(client, regular_user):
    resp = client.post("/api/auth/login", json={"email": "user@test.com", "password": "Test@1234"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, regular_user):
    resp = client.post("/api/auth/login", json={"email": "user@test.com", "password": "WrongPass"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "ghost@test.com", "password": "anything"})
    assert resp.status_code == 401


def test_get_profile(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user@test.com"
    assert data["role"] == "user"


def test_get_profile_no_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)


def test_get_profile_bad_token(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code in (401, 403)
