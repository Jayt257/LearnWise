"""
backend/tests/test_leaderboard.py
Tests for leaderboard endpoints:
  GET /api/leaderboard/{pair_id}
  GET /api/leaderboard/{pair_id}/friends

BUG EXPOSED: get_friends_leaderboard uses `or_` before it is imported
(NameError crash) — this test will FAIL before the fix, PASS after.
"""

import pytest

def register_user(client, username, email, password):
    return client.post("/api/auth/register", json={
        "username": username, "email": email,
        "password": password, "native_lang": "hi",
    })

def get_auth_headers(client, username, email, password):
    resp = register_user(client, username, email, password)
    if resp.status_code not in (200, 201):
        resp = client.post("/api/auth/login", json={"email": email, "password": password})
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}

PAIR_ID = "hi-en"


class TestGlobalLeaderboard:
    def test_leaderboard_empty(self, client, auth_headers):
        """Leaderboard for an empty pair returns empty list."""
        res = client.get(f"/api/leaderboard/{PAIR_ID}", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_leaderboard_shows_user_after_progress(self, client, auth_headers):
        """User appears on leaderboard after starting and completing an activity."""
        # Start a pair and complete an activity to generate XP
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_seq_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "month_number": 1,
            "block_number": 1,
            "score_earned": 75,
            "max_score": 100,
            "passed": True,
        })
        res = client.get(f"/api/leaderboard/{PAIR_ID}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        # First entry should have highest XP
        assert data[0]["total_xp"] >= 75

    def test_leaderboard_schema(self, client, auth_headers):
        """Leaderboard entries have required fields."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_seq_id": 2,
            "activity_type": "vocab",
            "lang_pair_id": PAIR_ID,
            "month_number": 1,
            "block_number": 1,
            "score_earned": 50,
            "max_score": 100,
            "passed": True,
        })
        res = client.get(f"/api/leaderboard/{PAIR_ID}", headers=auth_headers)
        assert res.status_code == 200
        if res.json():
            entry = res.json()[0]
            for field in ["rank", "user_id", "username", "total_xp"]:
                assert field in entry, f"Missing field: {field}"

    def test_leaderboard_sorted_by_xp(self, client):
        """Leaderboard is sorted by XP descending."""
        # Create two users with different XP
        headers1 = get_auth_headers(client, "lb_user1", "lb1@test.com", "SecurePass123")
        headers2 = get_auth_headers(client, "lb_user2", "lb2@test.com", "SecurePass123")

        client.post(f"/api/progress/{PAIR_ID}/start", headers=headers1)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=headers1, json={
            "activity_seq_id": 10,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "month_number": 1,
            "block_number": 2,
            "score_earned": 100,
            "max_score": 100,
            "passed": True,
        })
        client.post(f"/api/progress/{PAIR_ID}/start", headers=headers2)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=headers2, json={
            "activity_seq_id": 10,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "month_number": 1,
            "block_number": 2,
            "score_earned": 50,
            "max_score": 100,
            "passed": True,
        })

        res = client.get(f"/api/leaderboard/{PAIR_ID}", headers=headers1)
        assert res.status_code == 200
        scores = [e["total_xp"] for e in res.json()]
        assert scores == sorted(scores, reverse=True)

    def test_leaderboard_unauthenticated(self, client):
        """No token returns 401."""
        res = client.get(f"/api/leaderboard/{PAIR_ID}")
        assert res.status_code == 401


class TestFriendsLeaderboard:
    def test_friends_leaderboard_returns_list(self, client, auth_headers):
        """
        GET /api/leaderboard/{pair_id}/friends must return a list.
        BUG: Before fix, this causes NameError from missing `or_` import
        and returns 500.
        """
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        res = client.get(f"/api/leaderboard/{PAIR_ID}/friends", headers=auth_headers)
        # This FAILS with 500 before the leaderboard.py fix
        assert res.status_code == 200, (
            f"Expected 200, got {res.status_code}. "
            f"Bug: or_ used before import in leaderboard.py. "
            f"Response: {res.text}"
        )
        assert isinstance(res.json(), list)

    def test_friends_leaderboard_includes_self(self, client, auth_headers):
        """User appears in their own friends leaderboard."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_seq_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "month_number": 1,
            "block_number": 1,
            "score_earned": 60,
            "max_score": 100,
            "passed": True,
        })
        res = client.get(f"/api/leaderboard/{PAIR_ID}/friends", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

    def test_friends_leaderboard_unauthenticated(self, client):
        """No token returns 401."""
        res = client.get(f"/api/leaderboard/{PAIR_ID}/friends")
        assert res.status_code == 401
