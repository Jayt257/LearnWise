"""
backend/tests/test_users.py
Tests for user profile endpoints:
  GET  /api/users/me
  PUT  /api/users/me
  GET  /api/users/search
  GET  /api/users/{user_id}
  GET  /api/users/{user_id}/progress
"""

import uuid


class TestUserProfile:
    def test_get_my_profile(self, client, auth_headers):
        """GET /api/users/me returns current user's full profile."""
        res = client.get("/api/users/me", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "id" in data
        assert "username" in data
        assert "role" in data
        assert "created_at" in data

    def test_get_my_profile_unauthenticated(self, client):
        """GET /api/users/me without token returns 401."""
        res = client.get("/api/users/me")
        assert res.status_code == 401

    def test_update_profile_display_name(self, client, auth_headers):
        """PUT /api/users/me updates display_name."""
        res = client.put("/api/users/me", json={
            "display_name": "Updated Name",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["display_name"] == "Updated Name"

    def test_update_profile_native_lang(self, client, auth_headers):
        """PUT /api/users/me updates native_lang."""
        res = client.put("/api/users/me", json={
            "native_lang": "hi",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["native_lang"] == "hi"

    def test_update_profile_avatar_url(self, client, auth_headers):
        """PUT /api/users/me updates avatar_url."""
        res = client.put("/api/users/me", json={
            "avatar_url": "https://example.com/avatar.png",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["avatar_url"] == "https://example.com/avatar.png"

    def test_update_profile_unauthenticated(self, client):
        """PUT /api/users/me without token returns 401."""
        res = client.put("/api/users/me", json={"display_name": "Hacker"})
        assert res.status_code == 401


class TestUserSearch:
    def test_search_users_found(self, client, auth_headers):
        """GET /api/users/search?q=test returns matching users."""
        res = client.get("/api/users/search?q=test", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)

    def test_search_users_empty_result(self, client, auth_headers):
        """Search with no matches returns empty list."""
        res = client.get("/api/users/search?q=zzznobodyhasthisname", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["total"] == 0

    def test_search_requires_query(self, client, auth_headers):
        """Missing q parameter returns 422."""
        res = client.get("/api/users/search", headers=auth_headers)
        assert res.status_code == 422

    def test_search_unauthenticated(self, client):
        """Search without token returns 401."""
        res = client.get("/api/users/search?q=test")
        assert res.status_code == 401


class TestPublicUserProfile:
    def test_get_existing_user(self, client, auth_headers):
        """GET /api/users/{user_id} returns public profile."""
        # First get own ID
        me_res = client.get("/api/users/me", headers=auth_headers)
        user_id = me_res.json()["id"]

        res = client.get(f"/api/users/{user_id}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == user_id
        assert "username" in data
        # Public profile should NOT include email
        assert "email" not in data

    def test_get_nonexistent_user(self, client, auth_headers):
        """GET /api/users/{random_uuid} returns 404."""
        fake_id = str(uuid.uuid4())
        res = client.get(f"/api/users/{fake_id}", headers=auth_headers)
        assert res.status_code == 404

    def test_get_user_progress_public(self, client, auth_headers):
        """GET /api/users/{user_id}/progress returns progress list."""
        me_res = client.get("/api/users/me", headers=auth_headers)
        user_id = me_res.json()["id"]

        res = client.get(f"/api/users/{user_id}/progress", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "user" in data
        assert "progress" in data
        assert isinstance(data["progress"], list)
