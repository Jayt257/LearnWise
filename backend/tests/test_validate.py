"""
backend/tests/test_validate.py
Tests for activity validation endpoint:
  POST /api/validate
Tests MCQ local scoring, open-ended Groq fallback, error cases.
"""

import pytest
from unittest.mock import patch


PAIR_ID = "hi-en"


def _make_mcq_payload(activity_id=1):
    return {
        "activity_id": activity_id,
        "activity_type": "test",
        "lang_pair_id": PAIR_ID,
        "max_xp": 100,
        "user_lang": "hi",
        "target_lang": "en",
        "questions": [
            {
                "question_id": "q1",
                "block_type": "quiz",
                "user_answer": "0",
                "correct_answer": "0",
                "prompt": "What is hello in English?",
            },
            {
                "question_id": "q2",
                "block_type": "quiz",
                "user_answer": "1",
                "correct_answer": "2",
                "prompt": "What is goodbye in English?",
            },
        ]
    }


class TestValidateMCQ:
    def test_mcq_perfect_score(self, client, auth_headers):
        """Test activity with all correct answers gives 100%."""
        payload = {
            "activity_id": 1,
            "activity_type": "test",
            "lang_pair_id": PAIR_ID,
            "max_xp": 100,
            "user_lang": "hi",
            "target_lang": "en",
            "questions": [
                {
                    "question_id": "q1",
                    "block_type": "quiz",
                    "user_answer": "0",
                    "correct_answer": "0",
                },
                {
                    "question_id": "q2",
                    "block_type": "quiz",
                    "user_answer": "1",
                    "correct_answer": "1",
                },
            ]
        }
        res = client.post("/api/validate", json=payload, headers=auth_headers)
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["total_score"] == 100
        assert data["percentage"] == 100.0
        assert data["passed"] is True
        assert len(data["question_results"]) == 2
        assert all(q["correct"] for q in data["question_results"])

    def test_mcq_partial_score(self, client, auth_headers):
        """Test with some wrong answers gives partial score."""
        res = client.post("/api/validate", json=_make_mcq_payload(), headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        # 1 correct out of 2 → 50%
        assert data["percentage"] == 50.0
        assert data["passed"] is True  # 50% = threshold

    def test_mcq_all_wrong_fails(self, client, auth_headers):
        """All wrong answers → 0% → not passed."""
        payload = {
            "activity_id": 2,
            "activity_type": "test",
            "lang_pair_id": PAIR_ID,
            "max_xp": 100,
            "user_lang": "en",
            "target_lang": "hi",
            "questions": [
                {
                    "question_id": "q1",
                    "block_type": "quiz",
                    "user_answer": "3",
                    "correct_answer": "0",
                },
            ]
        }
        res = client.post("/api/validate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_score"] == 0
        assert data["passed"] is False

    def test_validate_response_schema(self, client, auth_headers):
        """Response includes all required fields."""
        res = client.post("/api/validate", json=_make_mcq_payload(), headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        for field in ["activity_id", "total_score", "max_score", "percentage",
                       "passed", "feedback", "suggestion", "question_results"]:
            assert field in data, f"Missing response field: {field}"

    def test_validate_empty_questions_rejected(self, client, auth_headers):
        """Empty questions list returns 400."""
        payload = {
            "activity_id": 1,
            "activity_type": "test",
            "lang_pair_id": PAIR_ID,
            "max_xp": 100,
            "user_lang": "en",
            "target_lang": "hi",
            "questions": []
        }
        res = client.post("/api/validate", json=payload, headers=auth_headers)
        assert res.status_code == 400

    def test_validate_missing_questions_field(self, client, auth_headers):
        """Missing questions field returns 422."""
        payload = {
            "activity_id": 1,
            "activity_type": "test",
            "lang_pair_id": PAIR_ID,
            "max_xp": 100,
        }
        res = client.post("/api/validate", json=payload, headers=auth_headers)
        assert res.status_code == 422

    def test_validate_unauthenticated(self, client):
        """No token returns 401."""
        res = client.post("/api/validate", json=_make_mcq_payload())
        assert res.status_code == 401


class TestValidateGroqFallback:
    """Tests open-ended types with Groq mocked to fallback."""

    def test_writing_uses_groq_or_fallback(self, client, auth_headers):
        """Writing activity goes through Groq path (mock fallback)."""
        with patch("app.services.groq_service.validate_activity") as mock_groq:
            mock_groq.return_value = {
                "question_results": [
                    {"question_id": "w1", "score": 80, "correct": True, "feedback": "Good!"}
                ],
                "overall_feedback": "Well written!",
                "suggestion": "Work on grammar.",
            }
            payload = {
                "activity_id": 3,
                "activity_type": "writing",
                "lang_pair_id": PAIR_ID,
                "max_xp": 100,
                "user_lang": "hi",
                "target_lang": "en",
                "questions": [
                    {
                        "question_id": "w1",
                        "block_type": "writing",
                        "user_answer": "I am going to the market.",
                        "prompt": "Describe your daily routine.",
                    }
                ]
            }
            res = client.post("/api/validate", json=payload, headers=auth_headers)
            assert res.status_code == 200
            data = res.json()
            assert data["total_score"] == 80
            assert data["passed"] is True
            assert mock_groq.called


class TestValidateEdgeCases:
    """Tests for edge cases, large inputs, and feedback tier logic."""

    def test_validate_max_questions_exceeded(self, client, auth_headers):
        """Reject requests with more than 50 questions."""
        payload = _make_mcq_payload()
        payload["questions"] = [payload["questions"][0].copy() for _ in range(51)]
        for i, q in enumerate(payload["questions"]):
            q["question_id"] = f"q{i}"
            
        res = client.post("/api/validate", json=payload, headers=auth_headers)
        assert res.status_code == 422
        assert "Too many questions" in res.text

    def test_validate_answer_length_exceeded(self, client, auth_headers):
        """Reject requests where a user_answer is > 2000 characters."""
        payload = _make_mcq_payload()
        payload["questions"][0]["user_answer"] = "A" * 2001
        
        res = client.post("/api/validate", json=payload, headers=auth_headers)
        assert res.status_code == 422
        assert "too long" in res.text.lower()

    def test_validate_feedback_tier_logic(self, client, auth_headers):
        """Test feedback_tier calculation based on score and attempt_count."""
        with patch("app.services.groq_service.validate_activity") as mock_groq:
            mock_groq.return_value = {
                "question_results": [{"question_id": "w1", "score": 40, "correct": False, "feedback": "Nope"}],
                "overall_feedback": "Try again",
                "suggestion": "Read chapter 1.",
            }
            
            # Scenario 1: Low score (<50%), 2nd attempt -> tier should be "hint"
            payload = {
                "activity_id": 3, "activity_type": "writing", "lang_pair_id": PAIR_ID,
                "max_xp": 100, "user_lang": "hi", "target_lang": "en",
                "attempt_count": 2,
                "questions": [{"question_id": "w1", "block_type": "writing", "user_answer": "bad"}]
            }
            res = client.post("/api/validate", json=payload, headers=auth_headers)
            assert res.status_code == 200
            assert res.json()["feedback_tier"] == "hint"

            # Scenario 2: High score (>=80%) -> tier should be "praise"
            mock_groq.return_value["question_results"][0]["score"] = 90
            res2 = client.post("/api/validate", json=payload, headers=auth_headers)
            assert res2.status_code == 200
            assert res2.json()["feedback_tier"] == "praise"
            
            # Scenario 3: Mid score (50-79%) -> tier should be "lesson"
            mock_groq.return_value["question_results"][0]["score"] = 65
            res3 = client.post("/api/validate", json=payload, headers=auth_headers)
            assert res3.status_code == 200
            assert res3.json()["feedback_tier"] == "lesson"
