import pytest
from app.schemas.activity import ValidateRequest, QuestionSubmission
from app.services import groq_service

# Note: We won't test live Groq API calls to avoid flakes and billing API usage in unit tests.
# Instead, we will test the internal functions that format prompts or schema validation logic
#, and test the router validation logic. 

def test_vocab_block_type_multiple_choice_is_accepted():
    """Ensure the schema accepts 'vocab' block_type after mapping."""
    # The frontend maps 'multiple_choice' to 'vocab'.
    req = ValidateRequest(
        activity_id=1,
        activity_type="vocab",
        lang_pair_id="hi-ja",
        max_xp=100,
        questions=[
            QuestionSubmission(
                question_id="vq_1",
                block_type="vocab",
                user_answer="A",
                correct_answer="A",
                prompt="Translate apple"
            )
        ]
    )
    assert req.questions[0].block_type == "vocab"
    
def test_groq_temperature_is_deterministic(monkeypatch):
    """Verify that Groq is called with temperature 0.1 for more deterministic results."""
    calls = []
    
    class MockChat:
        class completions:
            @staticmethod
            def create(model, messages, temperature, max_tokens):
                calls.append({"temp": temperature, "max_tokens": max_tokens})
                class MockChoice:
                    class message:
                        content = '{"question_results": [], "overall_feedback": "ok", "suggestion": "ok"}'
                class MockResponse:
                    choices = [MockChoice()]
                return MockResponse()
                
    class MockClient:
        chat = MockChat()
        
    monkeypatch.setattr(groq_service, "get_client", lambda: MockClient())
    
    # Call the service
    groq_service.validate_activity(
        activity_type="reading",
        questions=[],
        max_xp=100
    )
    
    # Check that temperature is indeed 0.1
    assert len(calls) == 1
    assert calls[0]["temp"] == 0.1

def test_romanization_context_included_in_prompt():
    """Verify the prompt explicitly tells the model to accept romanization (critical for CJK)."""
    prompt = groq_service._build_prompt(
        activity_type="vocab",
        questions=[],
        max_xp=100,
        user_lang="hi",
        target_lang="ja",
        feedback_tier="lesson"
    )
    
    assert "romanization/transliteration" in prompt
    assert "phonetic and semantic equivalence" in prompt

def test_lesson_comprehension_rubric_included():
    """Verify the specific lesson rubric allows paraphrasing."""
    prompt = groq_service._build_prompt(
        activity_type="lesson",
        questions=[],
        max_xp=100,
        user_lang="hi",
        target_lang="ja",
        feedback_tier="lesson"
    )
    assert "Accept paraphrases and romanized versions" in prompt

def test_pronunciation_partial_credit_rubric_included():
    """Verify the pronunciation rubric focuses on phonetic matches and ignores Whisper CJK bugs."""
    prompt = groq_service._build_prompt(
        activity_type="pronunciation",
        questions=[],
        max_xp=100,
        user_lang="hi",
        target_lang="ja",
        feedback_tier="lesson"
    )
    assert "Do NOT penalise Whisper's inability to output native CJK characters" in prompt
    assert "Compare the transcribed romanization to the target romanization" in prompt

def test_speaking_object_sample_response_no_500():
    """Verify string cast handles non-string user inputs gracefully to avoid 500s (e.g. from objects)."""
    # The frontend now uses `getSampleText(obj)` so it sends a string.
    # But if an object slips through to user_answer via API:
    q = QuestionSubmission(
        question_id="st_1",
        block_type="speaking",
        user_answer={"targetText": "ohayou"}, # Malformed client request
        correct_answer="ohayou"
    )
    prompt = groq_service._build_prompt(
        activity_type="speaking",
        questions=[q],
        max_xp=100,
        user_lang="en",
        target_lang="ja",
        feedback_tier="lesson"
    )
    # The prompt building should not crash and should stringify it
    assert "Student's answer: {'targetText': 'ohayou'}" in prompt
