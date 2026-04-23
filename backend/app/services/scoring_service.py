"""
backend/app/services/scoring_service.py
XP calculation and pass/fail determination.
Pass threshold = 50% of max_xp (configurable).

Bug Fix #14: Per-question scores are now clamped to [0, per_q_max] before
summing, preventing total_score from exceeding max_xp when Groq returns
out-of-range values.
"""

from typing import List
from app.schemas.activity import QuestionSubmission, QuestionResult

PASS_THRESHOLD = 0.5   # 50% — must score at least half to pass


def calculate_score(
    questions: List[QuestionSubmission],
    max_xp: int,
    groq_scores: List[dict],
) -> dict:
    """
    Aggregate Groq per-question scores into a total.
    Scores are clamped at the per-question level before summing (Bug Fix #14).
    Returns: {total_score, percentage, passed, question_results}
    """
    if max_xp == 0:
        # Edge case: activity worth 0 XP — auto-pass with 0 score
        return {
            "total_score": 0,
            "percentage": 100.0,
            "passed": True,
            "question_results": [
                QuestionResult(
                    question_id=q.get("question_id", "q"),
                    correct=q.get("correct", False),
                    score=0,
                    feedback=q.get("feedback"),
                )
                for q in groq_scores
            ],
        }

    num_q = len(groq_scores) if groq_scores else max(len(questions), 1)
    per_q_max = round(max_xp / num_q)

    question_results = []
    total = 0

    for q in groq_scores:
        raw_score = q.get("score", 0)
        # Ensure numeric
        if not isinstance(raw_score, (int, float)):
            raw_score = 0
        # Clamp to [0, per_q_max] — Bug Fix #14
        clamped = max(0, min(int(raw_score), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
                user_answer=q.get("user_answer"),
                correct_answer=q.get("correct_answer"),
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def score_mcq_locally(
    questions: List[QuestionSubmission],
    max_xp: int,
) -> dict:
    """
    Score multiple-choice and true/false questions locally (no Groq needed).
    user_answer = index (int or str); correct_answer = index (int or str).
    """
    if not questions:
        return {
            "total_score": 0,
            "percentage": 0.0,
            "passed": False,
            "question_results": [],
        }

    per_question_xp = round(max_xp / len(questions))
    groq_scores = []

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "user_answer": q.user_answer,
            "correct_answer": q.correct_answer,
            "feedback": (
                "Correct!"
                if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)
