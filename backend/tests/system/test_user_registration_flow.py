"""
tests/system/test_user_registration_flow.py
System / Acceptance Tests — User Registration & Authentication End-to-End Flow.
Black-box tests: exercises complete user journey from signup → login → profile access.
"""

import pytest


class TestUserRegistrationAcceptance:

    def test_complete_signup_then_login_flow(self, client):
        """TC-SYS-001: A new user can sign up and immediately log in."""
        r = client.post("/api/auth/register", json={
            "username": "sys_test_user",
            "email": "sys_test@learnwise.io",
            "password": "SecurePass123!"
        })
        assert r.status_code in (200, 201), f"Signup failed: {r.text}"

        # LoginRequest requires email + password (not username)
        r2 = client.post("/api/auth/login", json={
            "email": "sys_test@learnwise.io",
            "password": "SecurePass123!"
        })
        assert r2.status_code == 200, f"Login failed: {r2.text}"
        assert "access_token" in r2.json()

    def test_duplicate_registration_rejected(self, client):
        """TC-SYS-002: Registering the same username twice returns a 400 conflict."""
        data = {"username": "dup_sys_user", "email": "dup@learnwise.io", "password": "Pass123!"}
        client.post("/api/auth/register", json=data)
        r2 = client.post("/api/auth/register", json=data)
        assert r2.status_code in (400, 409, 422)

    def test_login_with_wrong_password_rejected(self, client):
        """TC-SYS-003: Logging in with wrong password returns 401 Unauthorized."""
        client.post("/api/auth/register", json={
            "username": "wrongpass_user", "email": "wp@learnwise.io", "password": "CorrectPass!"
        })
        r = client.post("/api/auth/login", json={
            "email": "wp@learnwise.io", "password": "WrongPass!"
        })
        assert r.status_code == 401

    def test_unauthenticated_profile_access_rejected(self, client):
        """TC-SYS-004: Accessing /api/users/me without token returns 401."""
        r = client.get("/api/users/me")
        assert r.status_code == 401

    def test_authenticated_profile_accessible(self, client, auth_headers):
        """TC-SYS-005: Authenticated user can access their profile."""
        r = client.get("/api/users/me", headers=auth_headers)
        assert r.status_code == 200
        assert "username" in r.json()

    def test_progress_accessible_after_login(self, client, auth_headers):
        """TC-SYS-006: Progress endpoint is accessible to authenticated user."""
        r = client.get("/api/progress", headers=auth_headers)
        assert r.status_code == 200


class TestHealthAndAvailability:

    def test_api_health_check_returns_ok(self, client):
        """TC-SYS-010: Health endpoint confirms platform is operational."""
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json().get("status") in ("ok", "healthy", "running")

    def test_docs_available(self, client):
        """TC-SYS-011: API docs endpoint is accessible (OpenAPI)."""
        r = client.get("/docs")
        assert r.status_code == 200
