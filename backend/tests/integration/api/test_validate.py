"""
backend/tests/test_validate.py
Validation endpoint tests: all activity types, SCORE_THRESHOLD_OVERRIDE=0.
All activities auto-pass when override=0.
"""
import pytest

BASE_Q = {
    "question_id": "q1",
    "block_type": "lesson",
    "user_answer": "Some answer",
    "correct_answer": "Correct answer",
    "prompt": "Test prompt here",
}

BASE = {
    "activity_id": 1,
    "lang_pair_id": "hi-ja",
    "max_xp": 50,
    "user_lang": "hi",
    "target_lang": "ja",
    "attempt_count": 1,
}


def test_validate_requires_auth(client):
    resp = client.post("/api/validate", json={**BASE, "activity_type": "lesson", "questions": [BASE_Q]})
    assert resp.status_code in (401, 403)


def test_validate_lesson(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "lesson", "questions": [BASE_Q],
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "total_score" in data
    assert "passed" in data
    assert data["passed"] is True           # SCORE_THRESHOLD_OVERRIDE=0


def test_validate_vocabulary(client, auth_headers):
    # Validate endpoint uses 'vocab' (short form) not 'vocabulary'
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "vocab",
        "questions": [{
            "question_id": "vq1", "block_type": "vocab",
            "user_answer": "inu", "correct_answer": "inu",
            "prompt": "What is the reading for 犬?",
        }],
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["passed"] is True


def test_validate_writing(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "writing",
        "questions": [{
            "question_id": "wq1", "block_type": "writing",
            "user_answer": "Watashi wa gakusei desu. Mainichi nihongo wo benkyou shimasu.",
            "correct_answer": "",
            "prompt": "Write a sentence about daily life.",
        }],
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["passed"] is True


def test_validate_pronunciation(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "pronunciation",
        "questions": [{
            "question_id": "pq1", "block_type": "pronunciation",
            "user_answer": "ohayou", "correct_answer": "おはよう",
            "prompt": "Pronounce: おはよう",
        }],
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["passed"] is True


def test_validate_listening(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "listening",
        "questions": [{
            "question_id": "lq1", "block_type": "multiple_choice",
            "user_answer": "Ohayou gozaimasu",
            "correct_answer": "Ohayou gozaimasu",
            "prompt": "What greeting was used in the morning?",
        }],
    })
    assert resp.status_code == 200, resp.text


def test_validate_speaking(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "speaking",
        "questions": [{
            "question_id": "sq1", "block_type": "speaking",
            "user_answer": "Watashi no namae wa Jeel desu.",
            "correct_answer": "Introduce yourself",
            "prompt": "Introduce yourself in Japanese.",
        }],
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["passed"] is True


def test_validate_reading(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "reading",
        "questions": [{
            "question_id": "rq1", "block_type": "short_answer",
            "user_answer": "The student greets the teacher in the morning.",
            "correct_answer": "Student says ohayou gozaimasu.",
            "prompt": "What happens in the passage?",
        }],
    })
    assert resp.status_code == 200, resp.text


def test_validate_test_mcq_local(client, auth_headers):
    """Test type uses local MCQ scoring (no Groq)."""
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "test",
        "questions": [
            {"question_id": "tq1", "block_type": "mcq",
             "user_answer": "かさ", "correct_answer": "かさ",
             "prompt": "Write kasa in hiragana"},
            {"question_id": "tq2", "block_type": "mcq",
             "user_answer": "wrong", "correct_answer": "correct",
             "prompt": "Another question"},
        ],
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "total_score" in data
    assert data["passed"] is True           # SCORE_THRESHOLD_OVERRIDE=0


def test_validate_empty_questions_rejected(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "lesson", "questions": [],
    })
    assert resp.status_code == 400


def test_validate_unknown_type_rejected(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "unknown_type", "questions": [BASE_Q],
    })
    assert resp.status_code == 422


def test_validate_response_structure(client, auth_headers):
    resp = client.post("/api/validate", headers=auth_headers, json={
        **BASE, "activity_type": "lesson", "questions": [BASE_Q],
    })
    assert resp.status_code == 200
    data = resp.json()
    required_keys = ["total_score", "max_score", "percentage", "passed",
                     "feedback", "suggestion", "question_results", "feedback_tier"]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"
