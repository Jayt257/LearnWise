"""
backend/app/routers/validate.py
Activity validation endpoint — sends user answers to Groq AI and returns scores.
  POST /api/validate  - Validate activity answers, get XP score + AI feedback

When SCORE_THRESHOLD_OVERRIDE=0 in .env, all activities auto-pass (for testing).
"""

from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.activity import ValidateRequest, ValidateResponse
from app.services import groq_service, scoring_service

router = APIRouter(prefix="/validate", tags=["Validation"])

# Activity types that use local MCQ scoring (fast, no Groq needed)
MCQ_TYPES = set()
# Activity types that use Groq AI evaluation
GROQ_TYPES = {"writing", "speaking", "pronunciation", "listening", "reading", "vocabulary", "vocab", "lesson", "test"}


@router.post("", response_model=ValidateResponse)
def validate_activity(
    req: ValidateRequest,
    current_user: User = Depends(get_current_user),
) -> ValidateResponse:
    """
    Validate user answers for any activity type.
    - MCQ/test: local scoring for speed + reliability
    - Open-ended: Groq AI evaluation
    - SCORE_THRESHOLD_OVERRIDE=0: always passes (testing mode)
    """
    if not req.questions:
        raise HTTPException(status_code=400, detail="No questions submitted")

    # Determine scoring strategy
    if req.activity_type in MCQ_TYPES:
        result = scoring_service.score_mcq_locally(req.questions, req.max_xp)
        overall_feedback = (
            "Great job on the test! You demonstrated solid knowledge." if result["passed"]
            else "Review the material carefully and try again!"
        )
        suggestion = "Focus on the questions you got wrong and revisit the lesson content."
        question_results = result["question_results"]

    else:
        # Groq AI evaluation
        groq_result = groq_service.validate_activity(
            activity_type=req.activity_type,
            questions=req.questions,
            max_xp=req.max_xp,
            user_lang=req.user_lang,
            target_lang=req.target_lang,
            attempt_count=req.attempt_count,
        )
        groq_scores = groq_result.get("question_results", [])
        result = scoring_service.calculate_score(req.questions, req.max_xp, groq_scores)
        overall_feedback = groq_result.get("overall_feedback", "Good effort!")
        suggestion = groq_result.get("suggestion", "Keep practicing!")
        question_results = result["question_results"]

    # Apply global score threshold override for testing (SCORE_THRESHOLD_OVERRIDE=0)
    effective_passed = result["passed"]
    if settings.SCORE_THRESHOLD_OVERRIDE >= 0:
        effective_passed = result["total_score"] >= settings.SCORE_THRESHOLD_OVERRIDE

    # Calculate feedback tier
    feedback_tier = groq_service._determine_feedback_tier(
        percentage=result["percentage"],
        attempt_count=req.attempt_count,
    )

    if req.activity_type in GROQ_TYPES and feedback_tier != "lesson":
        try:
            refined = groq_service.generate_tier_feedback(
                activity_type=req.activity_type,
                feedback_tier=feedback_tier,
                overall_feedback=overall_feedback,
                suggestion=suggestion,
                user_lang=req.user_lang,
                target_lang=req.target_lang,
            )
            overall_feedback = refined.get("overall_feedback", overall_feedback)
            suggestion = refined.get("suggestion", suggestion)
        except Exception:
            pass

    return ValidateResponse(
        activity_id=req.activity_id,
        total_score=result["total_score"],
        max_score=req.max_xp,
        percentage=result["percentage"],
        passed=effective_passed,
        feedback=overall_feedback,
        suggestion=suggestion,
        question_results=question_results,
        feedback_tier=feedback_tier,
    )
