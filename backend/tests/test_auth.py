"""
backend/tests/test_auth.py
Tests for authentication endpoints:
  POST /api/auth/register
  POST /api/auth/login
  POST /api/auth/admin/login
  GET  /api/auth/me
"""

import pytest


# ── Register ──────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self, client):
        """Valid registration returns 201 with token and user."""
        res = client.post("/api/auth/register", json={
            "username": "newuser1",
            "email": "newuser1@example.com",
            "password": "SecurePass123",
            "display_name": "New User",
            "native_lang": "en",
        })
        assert res.status_code == 201, res.text
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser1@example.com"
        assert data["user"]["username"] == "newuser1"
        assert data["user"]["role"] == "user"

    def test_register_duplicate_email(self, client):
        """Duplicate email returns 400."""
        payload = {
            "username": "user_a",
            "email": "dup@example.com",
            "password": "SecurePass123",
        }
        client.post("/api/auth/register", json=payload)
        payload2 = dict(payload)
        payload2["username"] = "user_b"
        res = client.post("/api/auth/register", json=payload2)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"].lower()

    def test_register_duplicate_username(self, client):
        """Duplicate username returns 400."""
        payload = {
            "username": "shared_name",
            "email": "first@example.com",
            "password": "SecurePass123",
        }
        client.post("/api/auth/register", json=payload)
        payload2 = dict(payload)
        payload2["email"] = "second@example.com"
        res = client.post("/api/auth/register", json=payload2)
        assert res.status_code == 400
        assert "already taken" in res.json()["detail"].lower()

    def test_register_weak_password(self, client):
        """Password shorter than 8 chars returns 422."""
        res = client.post("/api/auth/register", json={
            "username": "weakpass",
            "email": "weak@example.com",
            "password": "abc",
        })
        assert res.status_code == 422

    def test_register_invalid_username_chars(self, client):
        """Username with spaces returns 422."""
        res = client.post("/api/auth/register", json={
            "username": "bad user",
            "email": "bad@example.com",
            "password": "SecurePass123",
        })
        assert res.status_code == 422

    def test_register_invalid_email(self, client):
        """Malformed email returns 422."""
        res = client.post("/api/auth/register", json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "SecurePass123",
        })
        assert res.status_code == 422


# ── Login ─────────────────────────────────────────────────────

class TestLogin:
    def test_login_success(self, client):
        """Valid credentials return 200 with token."""
        client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "SecurePass123",
        })
        res = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "SecurePass123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Wrong password returns 401."""
        client.post("/api/auth/register", json={
            "username": "loginuser2",
            "email": "login2@example.com",
            "password": "SecurePass123",
        })
        res = client.post("/api/auth/login", json={
            "email": "login2@example.com",
            "password": "WrongPassword",
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        """Unregistered email returns 401."""
        res = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "SecurePass123",
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        """Missing password returns 422."""
        res = client.post("/api/auth/login", json={"email": "test@example.com"})
        assert res.status_code == 422


# ── Admin Login ───────────────────────────────────────────────

class TestAdminLogin:
    def test_admin_login_success(self, client, admin_headers):
        """Admin login with correct creds returns token."""
        res = client.post("/api/auth/admin/login", json={
            "email": "admin@learnwise.app",
            "password": "Admin@LearnWise2026",
        })
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert res.json()["user"]["role"] == "admin"

    def test_admin_login_wrong_password(self, client, admin_headers):
        """Admin login with wrong password returns 401."""
        res = client.post("/api/auth/admin/login", json={
            "email": "admin@learnwise.app",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_regular_user_cannot_admin_login(self, client):
        """Regular user account rejected from admin login endpoint."""
        client.post("/api/auth/register", json={
            "username": "regularuser",
            "email": "regular@example.com",
            "password": "SecurePass123",
        })
        res = client.post("/api/auth/admin/login", json={
            "email": "regular@example.com",
            "password": "SecurePass123",
        })
        assert res.status_code == 401


# ── /me ───────────────────────────────────────────────────────

class TestGetMe:
    def test_get_me_authenticated(self, client, auth_headers):
        """Authenticated user can get their own info."""
        res = client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data

    def test_get_me_unauthenticated(self, client):
        """No token returns 401."""
        res = client.get("/api/auth/me")
        assert res.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Garbage token returns 401."""
        res = client.get("/api/auth/me", headers={"Authorization": "Bearer bad.token.here"})
        assert res.status_code == 401
