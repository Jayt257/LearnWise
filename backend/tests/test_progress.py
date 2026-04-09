"""
backend/tests/test_progress.py
Tests for progress tracking endpoints:
  GET  /api/progress
  GET  /api/progress/{pair_id}
  POST /api/progress/{pair_id}/start
  POST /api/progress/{pair_id}/complete
  GET  /api/progress/{pair_id}/completions
"""

import pytest


PAIR_ID = "hi-en"


class TestGetAllProgress:
    def test_empty_progress(self, client, auth_headers):
        """New user has no progress records."""
        res = client.get("/api/progress", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_unauthenticated(self, client):
        """No token returns 401."""
        res = client.get("/api/progress")
        assert res.status_code == 401


class TestStartPair:
    def test_start_new_pair(self, client, auth_headers):
        """POST /api/progress/{pair_id}/start creates a new record with 201."""
        res = client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["lang_pair_id"] == PAIR_ID
        assert data["total_xp"] == 0
        assert data["current_month"] == 1
        assert data["current_week"] == 1
        assert data["current_activity_id"] == 1

    def test_start_existing_pair_returns_200(self, client, auth_headers):
        """Starting an already-started pair returns existing record (idempotent)."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        res = client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        # Should return existing record - either 201 or 200
        assert res.status_code in (200, 201)
        assert res.json()["lang_pair_id"] == PAIR_ID

    def test_start_pair_unauthenticated(self, client):
        """No token returns 401."""
        res = client.post(f"/api/progress/{PAIR_ID}/start")
        assert res.status_code == 401


class TestGetPairProgress:
    def test_get_progress_not_started(self, client, auth_headers):
        """Pair not started returns 404."""
        res = client.get(f"/api/progress/xx-yy", headers=auth_headers)
        assert res.status_code == 404

    def test_get_progress_after_start(self, client, auth_headers):
        """After starting, GET returns progress record."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        res = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["lang_pair_id"] == PAIR_ID
        # All required fields present
        for field in ["id", "user_id", "lang_pair_id", "total_xp",
                       "current_month", "current_week", "current_activity_id"]:
            assert field in data, f"Missing field: {field}"

    def test_get_all_progress_after_start(self, client, auth_headers):
        """After starting a pair, GET /api/progress shows it."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        res = client.get("/api/progress", headers=auth_headers)
        assert res.status_code == 200
        pair_ids = [p["lang_pair_id"] for p in res.json()]
        assert PAIR_ID in pair_ids


class TestCompleteActivity:
    def test_complete_activity_first_time(self, client, auth_headers):
        """Completing an activity for the first time awards XP."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        res = client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "score_earned": 80,
            "max_score": 100,
            "passed": True,
            "ai_feedback": "Great job!",
            "ai_suggestion": "Keep it up!",
        })
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["score_earned"] == 80
        assert data["passed"] is True
        assert data["attempts"] == 1

    def test_complete_activity_xp_increments(self, client, auth_headers):
        """XP is added to progress after completion."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "score_earned": 50,
            "max_score": 100,
            "passed": True,
        })
        progress_res = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
        assert progress_res.json()["total_xp"] == 50

    def test_complete_activity_no_xp_for_worse_score(self, client, auth_headers):
        """Retrying with a lower score does NOT add XP."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 2,
            "activity_type": "vocab",
            "lang_pair_id": PAIR_ID,
            "score_earned": 80,
            "max_score": 100,
            "passed": True,
        })
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 2,
            "activity_type": "vocab",
            "lang_pair_id": PAIR_ID,
            "score_earned": 50,
            "max_score": 100,
            "passed": True,
        })
        progress_res = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
        assert progress_res.json()["total_xp"] == 80  # stays at 80, not 130

    def test_complete_activity_xp_delta_on_improvement(self, client, auth_headers):
        """Retry with higher score adds only the delta."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 3,
            "activity_type": "reading",
            "lang_pair_id": PAIR_ID,
            "score_earned": 60,
            "max_score": 100,
            "passed": True,
        })
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 3,
            "activity_type": "reading",
            "lang_pair_id": PAIR_ID,
            "score_earned": 90,
            "max_score": 100,
            "passed": True,
        })
        progress_res = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
        assert progress_res.json()["total_xp"] == 90  # 60 + 30 delta


class TestGetCompletions:
    def test_get_completions_empty(self, client, auth_headers):
        """New pair has empty completions list."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        res = client.get(f"/api/progress/{PAIR_ID}/completions", headers=auth_headers)
        assert res.status_code == 200
        assert res.json() == []

    def test_get_completions_after_activity(self, client, auth_headers):
        """Completed activity appears in completions."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 5,
            "activity_type": "test",
            "lang_pair_id": PAIR_ID,
            "score_earned": 70,
            "max_score": 100,
            "passed": True,
        })
        res = client.get(f"/api/progress/{PAIR_ID}/completions", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["activity_id"] == 5
        assert data[0]["score_earned"] == 70
        # Verify schema fields
        for field in ["id", "activity_id", "activity_type", "score_earned",
                       "max_score", "passed", "attempts", "completed_at"]:
            assert field in data[0], f"Missing field: {field}"

class TestProgressLogic:
    def test_ai_feedback_storage(self, client, auth_headers):
        """Test that ai_feedback is stored in the completion record."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "score_earned": 100,
            "max_score": 100,
            "passed": True,
            "ai_feedback": "Perfect response!",
            "ai_suggestion": "Move to the next level."
        })
        res = client.get(f"/api/progress/{PAIR_ID}/completions", headers=auth_headers)
        data = res.json()
        assert data[0]["ai_feedback"] == "Perfect response!"
        assert data[0]["ai_suggestion"] == "Move to the next level."

    def test_activity_advance_logic_no_skip(self, client, auth_headers):
        """Regression for Bug #10: Completing a future activity does not skip current_activity_id."""
        client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
        
        # current_activity_id starts at 1. Let's complete activity 3.
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 3,
            "activity_type": "test",
            "lang_pair_id": PAIR_ID,
            "score_earned": 100,
            "max_score": 100,
            "passed": True,
        })
        
        res = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
        # Should remain at 1 because we didn't pass activity 1
        assert res.json()["current_activity_id"] == 1
        
        # Complete activity 1
        client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
            "activity_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": PAIR_ID,
            "score_earned": 100,
            "max_score": 100,
            "passed": True,
        })
        
        res = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
        # Now it advances to 2
        assert res.json()["current_activity_id"] == 2
