"""
tests/gui/test_gui_flows.py
GUI Testing — Simulates frontend page-level API interactions.
Models how the React frontend calls the API for each rendered page.
"""

import pytest


class TestLoginPageGUI:
    """GUI tests for the Login / Signup page."""

    def test_login_page_token_endpoint_returns_correct_shape(self, client):
        """GUI-001: Login form POST returns access_token + token_type."""
        client.post("/api/auth/register", json={
            "username": "gui_login_user",
            "email": "guilogin@learnwise.io",
            "password": "GUIPass123!"
        })
        # LoginRequest uses email + password (JSON body)
        r = client.post("/api/auth/login", json={
            "email": "guilogin@learnwise.io",
            "password": "GUIPass123!"
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_error_message_on_wrong_credentials(self, client):
        """GUI-002: Wrong credentials return 401."""
        r = client.post("/api/auth/login", json={
            "email": "nobody_gui@learnwise.io", "password": "badpass"
        })
        assert r.status_code == 401

    def test_register_form_missing_fields_rejected(self, client):
        """GUI-003: Incomplete registration form returns 422."""
        r = client.post("/api/auth/register", json={"username": "incomplete"})
        assert r.status_code == 422


class TestDashboardPageGUI:
    """GUI tests for the main Dashboard page."""

    def test_dashboard_loads_user_profile(self, client, auth_headers):
        """GUI-010: Dashboard fetches /api/users/me."""
        r = client.get("/api/users/me", headers=auth_headers)
        assert r.status_code == 200
        assert "username" in r.json()

    def test_dashboard_loads_progress(self, client, auth_headers):
        """GUI-011: Dashboard fetches /api/progress."""
        r = client.get("/api/progress", headers=auth_headers)
        assert r.status_code == 200

    def test_dashboard_loads_leaderboard(self, client, auth_headers):
        """GUI-012: Dashboard sidebar fetches leaderboard."""
        r = client.get("/api/leaderboard/hi-en", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_dashboard_redirects_unauthenticated(self, client):
        """GUI-013: Unauthenticated requests return 401."""
        assert client.get("/api/users/me").status_code == 401
        assert client.get("/api/progress").status_code == 401


class TestActivityPageGUI:
    """GUI tests for Activity pages."""

    def test_activity_validate_endpoint_accessible(self, client, auth_headers):
        """GUI-020: Empty POST to /api/validate returns 422 (validation error)."""
        r = client.post("/api/validate", json={}, headers=auth_headers)
        assert r.status_code == 422

    def test_activity_content_endpoint_reachable(self, client, auth_headers):
        """GUI-021: Content endpoint returns 200 or 404 for a pair."""
        r = client.get("/api/content/hi-en", headers=auth_headers)
        assert r.status_code in (200, 404)


class TestFriendsPageGUI:
    """GUI tests for the Friends / Social page."""

    def test_friends_list_renders(self, client, auth_headers):
        """GUI-030: Friends page loads successfully."""
        r = client.get("/api/friends", headers=auth_headers)
        assert r.status_code == 200
        body = r.json()
        # Response: {"friends": [...], "total": N}
        assert "friends" in body
        assert isinstance(body["friends"], list)

    def test_add_friend_missing_user_rejected(self, client, auth_headers):
        """GUI-031: Send friend request to non-existent user returns error."""
        r = client.post("/api/friends/request/99999", headers=auth_headers)
        assert r.status_code in (404, 400, 422)


class TestAdminPanelGUI:
    """GUI tests for the Admin Panel dashboard."""

    def test_admin_panel_loads_pairs(self, client, admin_headers):
        """GUI-040: Admin panel loads language pairs via /api/admin/languages."""
        r = client.get("/api/admin/languages", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_panel_loads_analytics(self, client, admin_headers):
        """GUI-041: Admin analytics dashboard endpoint returns 200."""
        r = client.get("/api/admin/analytics", headers=admin_headers)
        assert r.status_code == 200

    def test_admin_panel_blocked_for_regular_users(self, client, auth_headers):
        """GUI-042: Regular users see 403 Forbidden on admin routes."""
        r = client.get("/api/admin/languages", headers=auth_headers)
        assert r.status_code == 403
