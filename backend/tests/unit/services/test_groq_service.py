import pytest
import json
from app.services.groq_service import (
    validate_activity, 
    generate_tier_feedback, 
    _extract_json,
    _clamp_scores,
    _build_prompt
)
from app.schemas.activity import QuestionSubmission

def test_groq_extract_json_markdown():
    """Cover lines 195 for markdown fences"""
    markdown_str = "```json\n{\"test\": 1}\n```"
    result = _extract_json(markdown_str)
    assert result == {"test": 1}

def test_groq_clamp_score_invalid_type():
    """Cover line 215 for non-int/float scores"""
    results = [{"score": "not_a_number"}]
    clamped = _clamp_scores(results, 50)
    assert clamped[0]["score"] == 0

def test_groq_build_prompt_sample_answer():
    """Cover line 110 for sample_answer inclusion"""
    q = QuestionSubmission(
        question_id="q1",
        block_type="vocabulary",
        user_answer="test",
        correct_answer="test correct",
        sample_answer="test sample"
    )
    prompt = _build_prompt("vocabulary", [q], 100, "en", "hi")
    assert "Sample/expected answer: test sample" in prompt

def test_groq_validate_activity_broad_exception(monkeypatch):
    """Cover lines 277-279 broad Exception fallback"""
    import app.services.groq_service as gs
    
    def mock_get_client():
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        raise RuntimeError("Groq rate limit simulated")
        return MockClient()
        
    monkeypatch.setattr(gs, "get_client", mock_get_client)
    
    q = QuestionSubmission(
        question_id="q1",
        block_type="lesson",
        user_answer="dog",
        correct_answer="dog" # Will get 30% from fallback if incorrect, but here 100% since correct
    )
    res = validate_activity("lesson", [q], 10)
    # Fallback applied 
    assert "AI unavailable" in res["overall_feedback"]

def test_groq_generate_tier_feedback_exception(monkeypatch):
    """Cover lines 321-323 broad exception in generation"""
    import app.services.groq_service as gs
    
    def mock_get_client():
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        raise RuntimeError("Generation failure simulated")
        return MockClient()
        
    monkeypatch.setattr(gs, "get_client", mock_get_client)
    
    res = generate_tier_feedback("lesson", "praise", "orig overall", "orig sugg", "en", "hi")
    assert res["overall_feedback"] == "orig overall"
    assert res["suggestion"] == "orig sugg"

def test_groq_determine_feedback_tier():
    from app.services.groq_service import _determine_feedback_tier
    assert _determine_feedback_tier(85.0, 1) == "praise"
    assert _determine_feedback_tier(60.0, 1) == "lesson"
    assert _determine_feedback_tier(40.0, 2) == "hint"
    assert _determine_feedback_tier(40.0, 1) == "lesson"
    # Boundary: 55% is in the lesson band (>=50 and <80).
    # Mutation raises threshold to 60, so 55% falls to else → returns "hint" for >=2 attempts.
    # This assertion kills that mutant.
    assert _determine_feedback_tier(55.0, 1) == "lesson"
    assert _determine_feedback_tier(55.0, 2) == "lesson"  # NOT hint — still in lesson band
    assert _determine_feedback_tier(50.0, 2) == "lesson"  # exact boundary: >=50 → lesson

def test_groq_validate_activity_success_and_jsonerror(monkeypatch):
    import app.services.groq_service as gs
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
    
    class MockChoice:
        def __init__(self, content):
            self.message = MockMessage(content)

    class MockResponse:
        def __init__(self, content):
            self.choices = [MockChoice(content)]

    def mock_get_client():
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        # valid JSON but maybe with unexpected keys? No, valid JSON
                        return MockResponse('{"question_results": [{"score": 10}], "overall_feedback": "ok", "suggestion": "ok"}')
        return MockClient()
        
    monkeypatch.setattr(gs, "get_client", mock_get_client)
    
    q = QuestionSubmission(question_id="q1", block_type="lesson", user_answer="ans")
    res = validate_activity("lesson", [q], 10)
    assert res["overall_feedback"] == "ok"
    
    # Now simulate JSON Decode Error
    def mock_get_client_bad_json():
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        return MockResponse('NOT JSON AT ALL')
        return MockClient()
    
    monkeypatch.setattr(gs, "get_client", mock_get_client_bad_json)
    res2 = validate_activity("lesson", [q], 10)
    assert "AI unavailable" in res2["overall_feedback"]

def test_groq_get_client():
    import app.services.groq_service as gs
    # Ensure it's None to cover initialization
    gs._client = None
    client = gs.get_client()
    assert client is not None
    # Second call returns cached client
    assert gs.get_client() is client
