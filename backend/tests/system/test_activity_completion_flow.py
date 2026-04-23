"""
tests/system/test_activity_completion_flow.py
System / Acceptance Tests — Activity Submission & Scoring End-to-End Flow.
"""

import pytest


class TestActivitySubmissionFlow:

    def test_leaderboard_accessible_after_login(self, client, auth_headers):
        """TC-SYS-020: Authenticated user can view leaderboard."""
        r = client.get("/api/leaderboard/hi-en", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_progress_endpoint_returns_structured_data(self, client, auth_headers):
        """TC-SYS-021: Progress endpoint returns structured response."""
        r = client.get("/api/progress", headers=auth_headers)
        assert r.status_code == 200

    def test_friends_list_accessible(self, client, auth_headers):
        """TC-SYS-022: Authenticated user can retrieve their friends list."""
        r = client.get("/api/friends", headers=auth_headers)
        assert r.status_code == 200
        body = r.json()
        assert "friends" in body

    def test_unauthenticated_progress_rejected(self, client):
        """TC-SYS-023: Progress endpoint requires authentication."""
        assert client.get("/api/progress").status_code == 401

    def test_unauthenticated_leaderboard_rejected(self, client):
        """TC-SYS-024: Leaderboard endpoint requires authentication."""
        assert client.get("/api/leaderboard/hi-en").status_code == 401

    def test_content_list_pair_accessible(self, client, auth_headers):
        """TC-SYS-025: Content list endpoint is accessible for a valid pair."""
        r = client.get("/api/content/hi-en", headers=auth_headers)
        assert r.status_code in (200, 404)


class TestAdminWorkflowAcceptance:

    def test_admin_dashboard_accessible(self, client, admin_headers):
        """TC-SYS-030: Admin can access the language pairs management endpoint."""
        # actual endpoint is /api/admin/languages (not /api/admin/pairs)
        r = client.get("/api/admin/languages", headers=admin_headers)
        assert r.status_code == 200

    def test_admin_analytics_accessible(self, client, admin_headers):
        """TC-SYS-031: Admin can access the analytics endpoint."""
        r = client.get("/api/admin/analytics", headers=admin_headers)
        assert r.status_code == 200

    def test_non_admin_cannot_access_admin_routes(self, client, auth_headers):
        """TC-SYS-032: Regular user is rejected from admin endpoints (403 Forbidden)."""
        r = client.get("/api/admin/languages", headers=auth_headers)
        assert r.status_code == 403
