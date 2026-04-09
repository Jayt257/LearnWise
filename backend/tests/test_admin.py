"""
backend/tests/test_admin.py
Tests for admin-only endpoints:
  GET    /api/admin/stats
  GET    /api/admin/users
  PUT    /api/admin/users/{user_id}/role
  DELETE /api/admin/users/{user_id}
  GET    /api/admin/languages
  POST   /api/admin/languages
  DELETE /api/admin/languages/{pair_id}
  GET    /api/admin/content/{pair_id}
  PUT    /api/admin/content/{pair_id}
  PUT    /api/admin/content/{pair_id}/meta
  POST   /api/admin/content/{pair_id}/activity  (Bug 4 — missing endpoint)
"""

import json
import pytest
from pathlib import Path


# ── Patch data path for all admin content tests ───────────────

@pytest.fixture(autouse=True)
def patch_data_path(tmp_path, monkeypatch):
    from app.core import config
    monkeypatch.setattr(
        config.settings.__class__,
        "data_path",
        property(lambda self: str(tmp_path)),
    )
    monkeypatch.setattr("app.services.content_service.settings", config.settings)

    # Create a language_pairs.json
    lp_file = tmp_path / "language_pairs.json"
    lp_file.write_text("[]")
    yield tmp_path


# ── Stats ─────────────────────────────────────────────────────

class TestAdminStats:
    def test_stats_accessible_to_admin(self, client, admin_headers):
        """GET /api/admin/stats returns platform statistics."""
        res = client.get("/api/admin/stats", headers=admin_headers)
        assert res.status_code == 200, res.text
        data = res.json()
        for field in ["total_users", "active_today", "total_completions",
                       "total_xp_awarded", "language_pairs"]:
            assert field in data, f"Missing: {field}"

    def test_stats_forbidden_for_regular_user(self, client, auth_headers):
        """Regular user gets 403 on admin stats."""
        res = client.get("/api/admin/stats", headers=auth_headers)
        assert res.status_code == 403

    def test_stats_unauthenticated(self, client):
        """No token returns 401."""
        res = client.get("/api/admin/stats")
        assert res.status_code == 401


# ── User Management ───────────────────────────────────────────

class TestAdminUsers:
    def test_list_users(self, client, admin_headers):
        """GET /api/admin/users returns all users list."""
        res = client.get("/api/admin/users", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # at least admin
        # Verify schema
        for field in ["id", "username", "email", "role", "is_active"]:
            assert field in data[0], f"Missing: {field}"

    def test_list_users_forbidden_for_user(self, client, auth_headers):
        """Regular user gets 403."""
        res = client.get("/api/admin/users", headers=auth_headers)
        assert res.status_code == 403

    def test_update_user_role(self, client, admin_headers):
        """Admin can change a user's role."""
        # Register a regular user
        reg = client.post("/api/auth/register", json={
            "username": "roletestuser",
            "email": "roletest@example.com",
            "password": "SecurePass123",
        })
        user_id = reg.json()["user"]["id"]

        res = client.put(
            f"/api/admin/users/{user_id}/role",
            json={"role": "admin"},
            headers=admin_headers
        )
        assert res.status_code == 200
        assert "updated" in res.json()["message"].lower()

    def test_update_user_role_invalid(self, client, admin_headers):
        """Invalid role value returns 400."""
        reg = client.post("/api/auth/register", json={
            "username": "badrole",
            "email": "badrole@example.com",
            "password": "SecurePass123",
        })
        user_id = reg.json()["user"]["id"]
        res = client.put(
            f"/api/admin/users/{user_id}/role",
            json={"role": "superuser"},
            headers=admin_headers
        )
        assert res.status_code == 400

    def test_deactivate_user(self, client, admin_headers):
        """Admin can deactivate a user."""
        reg = client.post("/api/auth/register", json={
            "username": "deactivateme",
            "email": "deactivate@example.com",
            "password": "SecurePass123",
        })
        user_id = reg.json()["user"]["id"]

        res = client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)
        assert res.status_code == 200
        assert "deactivated" in res.json()["message"].lower()

    def test_deactivate_nonexistent_user(self, client, admin_headers):
        """Deactivating non-existent user returns 404."""
        import uuid
        res = client.delete(f"/api/admin/users/{uuid.uuid4()}", headers=admin_headers)
        assert res.status_code == 404


# ── Language Pairs ────────────────────────────────────────────

class TestAdminLanguages:
    def test_list_languages(self, client, admin_headers):
        """GET /api/admin/languages returns list."""
        res = client.get("/api/admin/languages", headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_create_language_pair(self, client, admin_headers):
        """POST /api/admin/languages creates a new pair."""
        res = client.post("/api/admin/languages", json={
            "source_lang_id": "te",
            "source_lang_name": "Test",
            "source_lang_flag": "🧪",
            "target_lang_id": "en",
            "target_lang_name": "English",
            "target_lang_flag": "🇬🇧",
        }, headers=admin_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["pair_id"] == "te-en"

    def test_create_language_pair_forbidden(self, client, auth_headers):
        """Regular user cannot create language pair."""
        res = client.post("/api/admin/languages", json={
            "source_lang_id": "xx",
            "source_lang_name": "X",
            "source_lang_flag": "🏳",
            "target_lang_id": "yy",
            "target_lang_name": "Y",
            "target_lang_flag": "🏳",
        }, headers=auth_headers)
        assert res.status_code == 403

    def test_delete_language_pair(self, client, admin_headers):
        """Admin can delete a language pair."""
        client.post("/api/admin/languages", json={
            "source_lang_id": "dl",
            "source_lang_name": "DeleteTest",
            "source_lang_flag": "🗑",
            "target_lang_id": "en",
            "target_lang_name": "English",
            "target_lang_flag": "🇬🇧",
        }, headers=admin_headers)

        res = client.delete("/api/admin/languages/dl-en", headers=admin_headers)
        assert res.status_code == 200


# ── Content Management ────────────────────────────────────────

class TestAdminContent:
    @pytest.fixture(autouse=True)
    def create_test_pair(self, client, admin_headers):
        """Create a test language pair for content tests."""
        client.post("/api/admin/languages", json={
            "source_lang_id": "ct",
            "source_lang_name": "ContentTest",
            "source_lang_flag": "📝",
            "target_lang_id": "en",
            "target_lang_name": "English",
            "target_lang_flag": "🇬🇧",
        }, headers=admin_headers)

    def test_list_content_files(self, client, admin_headers):
        """GET /api/admin/content/{pair_id} lists files."""
        res = client.get("/api/admin/content/ct-en", headers=admin_headers)
        assert res.status_code == 200
        assert "files" in res.json()

    def test_update_content_file(self, client, admin_headers):
        """PUT /api/admin/content/{pair_id} writes a content file."""
        res = client.put("/api/admin/content/ct-en", json={
            "file_path": "month-1/week-1-lesson.json",
            "content": {
                "activityId": 1,
                "type": "lesson",
                "title": "Test Lesson",
                "blocks": []
            }
        }, headers=admin_headers)
        assert res.status_code == 200
        assert "updated" in res.json()["message"].lower()

    def test_update_meta(self, client, admin_headers):
        """PUT /api/admin/content/{pair_id}/meta writes meta.json."""
        res = client.put("/api/admin/content/ct-en/meta", json={
            "file_path": "meta.json",
            "content": {
                "pairId": "ct-en",
                "source": {"id": "ct", "name": "ContentTest", "flag": "📝"},
                "target": {"id": "en", "name": "English", "flag": "🇬🇧"},
                "totalMonths": 3,
                "status": "active",
                "months": []
            }
        }, headers=admin_headers)
        assert res.status_code == 200

    def test_add_activity_file(self, client, admin_headers):
        """
        POST /api/admin/content/{pair_id}/activity adds a new activity file.
        BUG: This endpoint was MISSING before the fix — returns 404 or 405.
        After fix, should return 201.
        """
        res = client.post("/api/admin/content/ct-en/activity", json={
            "file_path": "month-1/week-2-vocab.json",
            "content": {
                "activityId": 2,
                "type": "vocab",
                "title": "Week 2 Vocab",
                "blocks": []
            }
        }, headers=admin_headers)
        # FAILS before fix (405 Method Not Allowed), PASSES after
        assert res.status_code == 201, (
            f"Expected 201, got {res.status_code}. "
            f"Bug: POST /admin/content/{{pair_id}}/activity endpoint was missing. "
            f"Response: {res.text}"
        )
        assert "created" in res.json()["message"].lower()

    def test_get_content_file(self, client, admin_headers):
        """GET /api/admin/content/{pair_id}/file?file=... returns file content."""
        # First write a file
        client.put("/api/admin/content/ct-en", json={
            "file_path": "month-1/week-1-lesson.json",
            "content": {"activityId": 1, "type": "lesson", "blocks": []}
        }, headers=admin_headers)
        res = client.get(
            "/api/admin/content/ct-en/file",
            params={"file": "month-1/week-1-lesson.json"},
            headers=admin_headers
        )
        assert res.status_code == 200
        assert res.json()["activityId"] == 1

    def test_content_forbidden_for_regular_user(self, client, auth_headers):
        """Regular user cannot access admin content endpoints."""
        res = client.get("/api/admin/content/ct-en", headers=auth_headers)
        assert res.status_code == 403


# ── Analytics and New Endpoints ────────────────────────────────

class TestAdminAnalyticsAndActivation:
    def test_get_analytics(self, client, admin_headers):
        """GET /api/admin/analytics returns detailed platform analytics."""
        res = client.get("/api/admin/analytics", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "activity_stats" in data
        assert "top_users" in data
        assert isinstance(data["activity_stats"], list)

    def test_activate_user(self, client, admin_headers):
        """PUT /api/admin/users/{user_id}/activate reactivates a user."""
        reg = client.post("/api/auth/register", json={
            "username": "reactivateme",
            "email": "reactivate@example.com",
            "password": "SecurePass123",
        })
        user_id = reg.json()["user"]["id"]

        # Deactivate first
        client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)
        
        # Reactivate
        res = client.put(f"/api/admin/users/{user_id}/activate", headers=admin_headers)
        assert res.status_code == 200
        assert "activated" in res.json()["message"].lower()

    def test_get_activity_types(self, client, admin_headers):
        """GET /api/admin/activity-types returns types and templates."""
        res = client.get("/api/admin/activity-types", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "activity_types" in data
        assert "templates" in data
        assert any(t["id"] == "lesson" for t in data["activity_types"])
