import pytest
from unittest.mock import patch, MagicMock
from app.services import groq_service, whisper_service
from app.schemas.activity import QuestionSubmission

@pytest.fixture
def auth_headers(client):
    # Register and login first to get a token
    client.post("/api/auth/register", json={
        "username": "finalcov", "email": "finalcov@learnwise.io", "password": "Pass123!"
    })
    r = client.post("/api/auth/login", json={
        "email": "finalcov@learnwise.io", "password": "Pass123!"
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_progress_with_threshold_override(client, auth_headers, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "SCORE_THRESHOLD_OVERRIDE", 80)
    
    client.post("/api/progress/hi-ja/start", headers=auth_headers)

    # Needs a real activity_seq_id format
    data = {
        "activity_seq_id": 998,
        "activity_type": "reading",
        "lang_pair_id": "hi-ja",
        "month_number": 1,
        "block_number": 1,
        "passed": False, 
        "score_earned": 85,
        "max_score": 100
    }
    # User got 85 score, override is 80, so it's effectively passed even though passed is False
    res = client.post("/api/progress/hi-ja/complete", json=data, headers=auth_headers)
    assert res.status_code in (200, 201)

def test_validate_mcq_logic(client, auth_headers):
    # test activity_type -> MCQ_TYPES
    data = {
        "activity_id": 999,
        "activity_type": "test",
        "lang_pair_id": "hi-ja",
        "max_xp": 100,
        "questions": [
            {
                "question_id": "q1",
                "block_type": "test",
                "user_answer": "A",
                "correct_answer": "A",
                "prompt": "Q1"
            }
        ]
    }
    res = client.post("/api/validate", json=data, headers=auth_headers)
    assert res.status_code == 200
    j = res.json()
    assert j["passed"] is True
    assert j["total_score"] == 100

def test_validate_with_threshold_override(client, auth_headers, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "SCORE_THRESHOLD_OVERRIDE", 90)
    
    # 50% score
    data = {
        "activity_id": 999,
        "activity_type": "test",
        "lang_pair_id": "hi-ja",
        "max_xp": 100,
        "questions": [
            {
                "question_id": "q1",
                "block_type": "test",
                "user_answer": "A",
                "correct_answer": "A",
                "prompt": "Q1"
            },
            {
                "question_id": "q2",
                "block_type": "test",
                "user_answer": "B",
                "correct_answer": "A",
                "prompt": "Q2"
            }
        ]
    }
    res = client.post("/api/validate", json=data, headers=auth_headers)
    assert res.status_code == 200
    # Normally 50% fails because threshold is 0.2
    # Wait, with threshold=90, 50 < 90 so it should fail
    # Actually, default MCQ is pass directly? No, calculate_score is used in logic.
    assert res.json()["passed"] is False

def test_groq_service_merges_user_answer(monkeypatch):
    # Mock groq response to have matching question_id
    class MockChat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                class MockChoice:
                    class message:
                        content = '{"question_results": [{"question_id": "q1", "score": 100}], "overall_feedback": "ok", "suggestion": "ok"}'
                class MockResponse:
                    choices = [MockChoice()]
                return MockResponse()
                
    class MockClient:
        chat = MockChat()
        
    monkeypatch.setattr(groq_service, "get_client", lambda: MockClient())
    
    questions = [
        QuestionSubmission(
            question_id="q1",
            block_type="reading",
            user_answer="my answer",
            correct_answer="correct ans"
        )
    ]
    
    res = groq_service.validate_activity("reading", questions, 100)
    assert res["question_results"][0]["user_answer"] == "my answer"
    assert res["question_results"][0]["correct_answer"] == "correct ans"

def test_whisper_unavailable_returns_mock(monkeypatch):
    # Force _load_model to return False
    monkeypatch.setattr(whisper_service, "_load_model", lambda: False)
    # Give a dummy temp file path
    res = whisper_service.transcribe_audio("dummy.webm")
    assert res["is_mock"] is True
    assert res["text"] == ""
