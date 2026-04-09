"""
backend/app/schemas/activity.py
Pydantic schemas for activity validation requests and responses.
Used by POST /api/validate endpoint.

Changes:
- Added `attempt_count` to ValidateRequest for feedback tier calculation
- Added `feedback_tier` to ValidateResponse (hint | lesson | praise)
- Added `is_mock` to TranscribeResponse for Whisper fallback detection
- Added `max_answer_length` validator on QuestionSubmission
"""

from pydantic import BaseModel, field_validator
from typing import Optional, List, Any

MAX_ANSWER_LENGTH = 2000    # characters — guards Groq token overflow
MAX_QUESTIONS = 50          # max questions per submission


class QuestionSubmission(BaseModel):
    """A single question/block answer from the user."""
    question_id: str                # block id e.g. "b1"
    block_type: str                 # quiz | fill_blank | writing | speaking | etc.
    user_answer: Any                # string, int (option index), or list
    correct_answer: Optional[Any] = None   # admin-defined correct answer
    prompt: Optional[str] = None   # for open-ended types
    sample_answer: Optional[str] = None

    @field_validator("user_answer")
    @classmethod
    def validate_answer_length(cls, v: Any) -> Any:
        """Prevent token overflow: cap string answers at MAX_ANSWER_LENGTH chars."""
        if isinstance(v, str) and len(v) > MAX_ANSWER_LENGTH:
            raise ValueError(
                f"Answer is too long ({len(v)} chars). "
                f"Maximum allowed is {MAX_ANSWER_LENGTH} characters."
            )
        return v

    @field_validator("prompt")
    @classmethod
    def validate_prompt_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > MAX_ANSWER_LENGTH:
            raise ValueError(f"Prompt exceeds {MAX_ANSWER_LENGTH} character limit.")
        return v


class ValidateRequest(BaseModel):
    activity_id: int
    activity_type: str              # lesson | vocab | reading | writing | listening | speaking | pronunciation | test
    lang_pair_id: str
    max_xp: int
    user_lang: str = "hi"          # native language for feedback
    target_lang: str = "en"        # language being learned
    questions: List[QuestionSubmission]
    attempt_count: int = 1         # how many times user has attempted this activity (for feedback tier)

    @field_validator("questions")
    @classmethod
    def validate_questions_count(cls, v: list) -> list:
        if len(v) > MAX_QUESTIONS:
            raise ValueError(
                f"Too many questions ({len(v)}). Maximum allowed is {MAX_QUESTIONS}."
            )
        return v

    @field_validator("max_xp")
    @classmethod
    def validate_max_xp(cls, v: int) -> int:
        if v < 0:
            raise ValueError("max_xp cannot be negative.")
        return v

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, v: str) -> str:
        allowed = {"lesson", "vocab", "reading", "writing", "listening", "speaking", "pronunciation", "test"}
        if v not in allowed:
            raise ValueError(f"Unknown activity_type '{v}'. Must be one of: {', '.join(sorted(allowed))}")
        return v


class QuestionResult(BaseModel):
    question_id: str
    correct: bool
    score: int
    feedback: Optional[str] = None


class ValidateResponse(BaseModel):
    activity_id: int
    total_score: int
    max_score: int
    percentage: float
    passed: bool
    feedback: str                   # Overall Groq feedback
    suggestion: str                 # Improvement tip
    question_results: List[QuestionResult]
    feedback_tier: str = "lesson"   # hint | lesson | praise — drives notification UI


class TranscribeResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    is_mock: bool = False           # True when Whisper not installed (dev fallback)
