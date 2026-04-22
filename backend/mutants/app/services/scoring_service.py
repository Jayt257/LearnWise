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

PASS_THRESHOLD = 0.0   # 0%
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


def calculate_score(
    questions: List[QuestionSubmission],
    max_xp: int,
    groq_scores: List[dict],
) -> dict:
    args = [questions, max_xp, groq_scores]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_calculate_score__mutmut_orig, x_calculate_score__mutmut_mutants, args, kwargs, None)


def x_calculate_score__mutmut_orig(
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


def x_calculate_score__mutmut_1(
    questions: List[QuestionSubmission],
    max_xp: int,
    groq_scores: List[dict],
) -> dict:
    """
    Aggregate Groq per-question scores into a total.
    Scores are clamped at the per-question level before summing (Bug Fix #14).
    Returns: {total_score, percentage, passed, question_results}
    """
    if max_xp != 0:
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


def x_calculate_score__mutmut_2(
    questions: List[QuestionSubmission],
    max_xp: int,
    groq_scores: List[dict],
) -> dict:
    """
    Aggregate Groq per-question scores into a total.
    Scores are clamped at the per-question level before summing (Bug Fix #14).
    Returns: {total_score, percentage, passed, question_results}
    """
    if max_xp == 1:
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


def x_calculate_score__mutmut_3(
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
            "XXtotal_scoreXX": 0,
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


def x_calculate_score__mutmut_4(
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
            "TOTAL_SCORE": 0,
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


def x_calculate_score__mutmut_5(
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
            "total_score": 1,
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


def x_calculate_score__mutmut_6(
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
            "XXpercentageXX": 100.0,
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


def x_calculate_score__mutmut_7(
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
            "PERCENTAGE": 100.0,
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


def x_calculate_score__mutmut_8(
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
            "percentage": 101.0,
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


def x_calculate_score__mutmut_9(
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
            "XXpassedXX": True,
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


def x_calculate_score__mutmut_10(
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
            "PASSED": True,
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


def x_calculate_score__mutmut_11(
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
            "passed": False,
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


def x_calculate_score__mutmut_12(
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
            "XXquestion_resultsXX": [
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


def x_calculate_score__mutmut_13(
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
            "QUESTION_RESULTS": [
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


def x_calculate_score__mutmut_14(
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
                    question_id=None,
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


def x_calculate_score__mutmut_15(
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
                    correct=None,
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


def x_calculate_score__mutmut_16(
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
                    score=None,
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


def x_calculate_score__mutmut_17(
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
                    feedback=None,
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


def x_calculate_score__mutmut_18(
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


def x_calculate_score__mutmut_19(
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


def x_calculate_score__mutmut_20(
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


def x_calculate_score__mutmut_21(
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


def x_calculate_score__mutmut_22(
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
                    question_id=q.get(None, "q"),
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


def x_calculate_score__mutmut_23(
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
                    question_id=q.get("question_id", None),
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


def x_calculate_score__mutmut_24(
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
                    question_id=q.get("q"),
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


def x_calculate_score__mutmut_25(
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
                    question_id=q.get("question_id", ),
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


def x_calculate_score__mutmut_26(
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
                    question_id=q.get("XXquestion_idXX", "q"),
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


def x_calculate_score__mutmut_27(
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
                    question_id=q.get("QUESTION_ID", "q"),
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


def x_calculate_score__mutmut_28(
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
                    question_id=q.get("question_id", "XXqXX"),
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


def x_calculate_score__mutmut_29(
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
                    question_id=q.get("question_id", "Q"),
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


def x_calculate_score__mutmut_30(
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
                    correct=q.get(None, False),
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


def x_calculate_score__mutmut_31(
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
                    correct=q.get("correct", None),
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


def x_calculate_score__mutmut_32(
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
                    correct=q.get(False),
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


def x_calculate_score__mutmut_33(
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
                    correct=q.get("correct", ),
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


def x_calculate_score__mutmut_34(
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
                    correct=q.get("XXcorrectXX", False),
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


def x_calculate_score__mutmut_35(
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
                    correct=q.get("CORRECT", False),
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


def x_calculate_score__mutmut_36(
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
                    correct=q.get("correct", True),
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


def x_calculate_score__mutmut_37(
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
                    score=1,
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


def x_calculate_score__mutmut_38(
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
                    feedback=q.get(None),
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


def x_calculate_score__mutmut_39(
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
                    feedback=q.get("XXfeedbackXX"),
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


def x_calculate_score__mutmut_40(
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
                    feedback=q.get("FEEDBACK"),
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


def x_calculate_score__mutmut_41(
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

    num_q = None
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


def x_calculate_score__mutmut_42(
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

    num_q = len(groq_scores) if groq_scores else max(None, 1)
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


def x_calculate_score__mutmut_43(
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

    num_q = len(groq_scores) if groq_scores else max(len(questions), None)
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


def x_calculate_score__mutmut_44(
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

    num_q = len(groq_scores) if groq_scores else max(1)
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


def x_calculate_score__mutmut_45(
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

    num_q = len(groq_scores) if groq_scores else max(len(questions), )
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


def x_calculate_score__mutmut_46(
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

    num_q = len(groq_scores) if groq_scores else max(len(questions), 2)
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


def x_calculate_score__mutmut_47(
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
    per_q_max = None

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


def x_calculate_score__mutmut_48(
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
    per_q_max = round(None)

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


def x_calculate_score__mutmut_49(
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
    per_q_max = round(max_xp * num_q)

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


def x_calculate_score__mutmut_50(
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

    question_results = None
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


def x_calculate_score__mutmut_51(
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
    total = None

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


def x_calculate_score__mutmut_52(
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
    total = 1

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


def x_calculate_score__mutmut_53(
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
        raw_score = None
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


def x_calculate_score__mutmut_54(
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
        raw_score = q.get(None, 0)
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


def x_calculate_score__mutmut_55(
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
        raw_score = q.get("score", None)
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


def x_calculate_score__mutmut_56(
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
        raw_score = q.get(0)
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


def x_calculate_score__mutmut_57(
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
        raw_score = q.get("score", )
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


def x_calculate_score__mutmut_58(
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
        raw_score = q.get("XXscoreXX", 0)
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


def x_calculate_score__mutmut_59(
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
        raw_score = q.get("SCORE", 0)
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


def x_calculate_score__mutmut_60(
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
        raw_score = q.get("score", 1)
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


def x_calculate_score__mutmut_61(
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
        if isinstance(raw_score, (int, float)):
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


def x_calculate_score__mutmut_62(
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
            raw_score = None
        # Clamp to [0, per_q_max] — Bug Fix #14
        clamped = max(0, min(int(raw_score), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_63(
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
            raw_score = 1
        # Clamp to [0, per_q_max] — Bug Fix #14
        clamped = max(0, min(int(raw_score), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_64(
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
        clamped = None
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_65(
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
        clamped = max(None, min(int(raw_score), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_66(
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
        clamped = max(0, None)
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_67(
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
        clamped = max(min(int(raw_score), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_68(
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
        clamped = max(0, )
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_69(
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
        clamped = max(1, min(int(raw_score), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_70(
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
        clamped = max(0, min(None, per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_71(
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
        clamped = max(0, min(int(raw_score), None))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_72(
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
        clamped = max(0, min(per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_73(
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
        clamped = max(0, min(int(raw_score), ))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_74(
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
        clamped = max(0, min(int(None), per_q_max))
        total += clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_75(
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
        total = clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_76(
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
        total -= clamped
        question_results.append(
            QuestionResult(
                question_id=q.get("question_id", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_77(
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
            None
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


def x_calculate_score__mutmut_78(
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
                question_id=None,
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_79(
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
                correct=None,
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_80(
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
                score=None,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_81(
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
                feedback=None,
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


def x_calculate_score__mutmut_82(
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
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_83(
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
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_84(
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
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_85(
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


def x_calculate_score__mutmut_86(
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
                question_id=q.get(None, "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_87(
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
                question_id=q.get("question_id", None),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_88(
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
                question_id=q.get("unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_89(
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
                question_id=q.get("question_id", ),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_90(
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
                question_id=q.get("XXquestion_idXX", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_91(
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
                question_id=q.get("QUESTION_ID", "unknown"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_92(
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
                question_id=q.get("question_id", "XXunknownXX"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_93(
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
                question_id=q.get("question_id", "UNKNOWN"),
                correct=bool(q.get("correct", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_94(
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
                correct=bool(None),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_95(
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
                correct=bool(q.get(None, False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_96(
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
                correct=bool(q.get("correct", None)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_97(
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
                correct=bool(q.get(False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_98(
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
                correct=bool(q.get("correct", )),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_99(
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
                correct=bool(q.get("XXcorrectXX", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_100(
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
                correct=bool(q.get("CORRECT", False)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_101(
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
                correct=bool(q.get("correct", True)),
                score=clamped,
                feedback=q.get("feedback"),
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


def x_calculate_score__mutmut_102(
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
                feedback=q.get(None),
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


def x_calculate_score__mutmut_103(
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
                feedback=q.get("XXfeedbackXX"),
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


def x_calculate_score__mutmut_104(
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
                feedback=q.get("FEEDBACK"),
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


def x_calculate_score__mutmut_105(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = None
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_106(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(None, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_107(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, None)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_108(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_109(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, )
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_110(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = None
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_111(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round(None, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_112(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, None)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_113(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round(1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_114(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, )
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_115(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) / 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_116(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total * max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_117(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 101, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_118(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 2)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_119(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = None

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_120(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage > (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_121(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD / 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_122(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 101)

    return {
        "total_score": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_123(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "XXtotal_scoreXX": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_124(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "TOTAL_SCORE": total,
        "percentage": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_125(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "XXpercentageXX": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_126(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "PERCENTAGE": percentage,
        "passed": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_127(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "XXpassedXX": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_128(
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
            )
        )

    # Final cap at max_xp (handles rounding drift)
    total = min(total, max_xp)
    percentage = round((total / max_xp) * 100, 1)
    passed = percentage >= (PASS_THRESHOLD * 100)

    return {
        "total_score": total,
        "percentage": percentage,
        "PASSED": passed,
        "question_results": question_results,
    }


def x_calculate_score__mutmut_129(
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
        "XXquestion_resultsXX": question_results,
    }


def x_calculate_score__mutmut_130(
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
        "QUESTION_RESULTS": question_results,
    }

x_calculate_score__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_calculate_score__mutmut_1': x_calculate_score__mutmut_1, 
    'x_calculate_score__mutmut_2': x_calculate_score__mutmut_2, 
    'x_calculate_score__mutmut_3': x_calculate_score__mutmut_3, 
    'x_calculate_score__mutmut_4': x_calculate_score__mutmut_4, 
    'x_calculate_score__mutmut_5': x_calculate_score__mutmut_5, 
    'x_calculate_score__mutmut_6': x_calculate_score__mutmut_6, 
    'x_calculate_score__mutmut_7': x_calculate_score__mutmut_7, 
    'x_calculate_score__mutmut_8': x_calculate_score__mutmut_8, 
    'x_calculate_score__mutmut_9': x_calculate_score__mutmut_9, 
    'x_calculate_score__mutmut_10': x_calculate_score__mutmut_10, 
    'x_calculate_score__mutmut_11': x_calculate_score__mutmut_11, 
    'x_calculate_score__mutmut_12': x_calculate_score__mutmut_12, 
    'x_calculate_score__mutmut_13': x_calculate_score__mutmut_13, 
    'x_calculate_score__mutmut_14': x_calculate_score__mutmut_14, 
    'x_calculate_score__mutmut_15': x_calculate_score__mutmut_15, 
    'x_calculate_score__mutmut_16': x_calculate_score__mutmut_16, 
    'x_calculate_score__mutmut_17': x_calculate_score__mutmut_17, 
    'x_calculate_score__mutmut_18': x_calculate_score__mutmut_18, 
    'x_calculate_score__mutmut_19': x_calculate_score__mutmut_19, 
    'x_calculate_score__mutmut_20': x_calculate_score__mutmut_20, 
    'x_calculate_score__mutmut_21': x_calculate_score__mutmut_21, 
    'x_calculate_score__mutmut_22': x_calculate_score__mutmut_22, 
    'x_calculate_score__mutmut_23': x_calculate_score__mutmut_23, 
    'x_calculate_score__mutmut_24': x_calculate_score__mutmut_24, 
    'x_calculate_score__mutmut_25': x_calculate_score__mutmut_25, 
    'x_calculate_score__mutmut_26': x_calculate_score__mutmut_26, 
    'x_calculate_score__mutmut_27': x_calculate_score__mutmut_27, 
    'x_calculate_score__mutmut_28': x_calculate_score__mutmut_28, 
    'x_calculate_score__mutmut_29': x_calculate_score__mutmut_29, 
    'x_calculate_score__mutmut_30': x_calculate_score__mutmut_30, 
    'x_calculate_score__mutmut_31': x_calculate_score__mutmut_31, 
    'x_calculate_score__mutmut_32': x_calculate_score__mutmut_32, 
    'x_calculate_score__mutmut_33': x_calculate_score__mutmut_33, 
    'x_calculate_score__mutmut_34': x_calculate_score__mutmut_34, 
    'x_calculate_score__mutmut_35': x_calculate_score__mutmut_35, 
    'x_calculate_score__mutmut_36': x_calculate_score__mutmut_36, 
    'x_calculate_score__mutmut_37': x_calculate_score__mutmut_37, 
    'x_calculate_score__mutmut_38': x_calculate_score__mutmut_38, 
    'x_calculate_score__mutmut_39': x_calculate_score__mutmut_39, 
    'x_calculate_score__mutmut_40': x_calculate_score__mutmut_40, 
    'x_calculate_score__mutmut_41': x_calculate_score__mutmut_41, 
    'x_calculate_score__mutmut_42': x_calculate_score__mutmut_42, 
    'x_calculate_score__mutmut_43': x_calculate_score__mutmut_43, 
    'x_calculate_score__mutmut_44': x_calculate_score__mutmut_44, 
    'x_calculate_score__mutmut_45': x_calculate_score__mutmut_45, 
    'x_calculate_score__mutmut_46': x_calculate_score__mutmut_46, 
    'x_calculate_score__mutmut_47': x_calculate_score__mutmut_47, 
    'x_calculate_score__mutmut_48': x_calculate_score__mutmut_48, 
    'x_calculate_score__mutmut_49': x_calculate_score__mutmut_49, 
    'x_calculate_score__mutmut_50': x_calculate_score__mutmut_50, 
    'x_calculate_score__mutmut_51': x_calculate_score__mutmut_51, 
    'x_calculate_score__mutmut_52': x_calculate_score__mutmut_52, 
    'x_calculate_score__mutmut_53': x_calculate_score__mutmut_53, 
    'x_calculate_score__mutmut_54': x_calculate_score__mutmut_54, 
    'x_calculate_score__mutmut_55': x_calculate_score__mutmut_55, 
    'x_calculate_score__mutmut_56': x_calculate_score__mutmut_56, 
    'x_calculate_score__mutmut_57': x_calculate_score__mutmut_57, 
    'x_calculate_score__mutmut_58': x_calculate_score__mutmut_58, 
    'x_calculate_score__mutmut_59': x_calculate_score__mutmut_59, 
    'x_calculate_score__mutmut_60': x_calculate_score__mutmut_60, 
    'x_calculate_score__mutmut_61': x_calculate_score__mutmut_61, 
    'x_calculate_score__mutmut_62': x_calculate_score__mutmut_62, 
    'x_calculate_score__mutmut_63': x_calculate_score__mutmut_63, 
    'x_calculate_score__mutmut_64': x_calculate_score__mutmut_64, 
    'x_calculate_score__mutmut_65': x_calculate_score__mutmut_65, 
    'x_calculate_score__mutmut_66': x_calculate_score__mutmut_66, 
    'x_calculate_score__mutmut_67': x_calculate_score__mutmut_67, 
    'x_calculate_score__mutmut_68': x_calculate_score__mutmut_68, 
    'x_calculate_score__mutmut_69': x_calculate_score__mutmut_69, 
    'x_calculate_score__mutmut_70': x_calculate_score__mutmut_70, 
    'x_calculate_score__mutmut_71': x_calculate_score__mutmut_71, 
    'x_calculate_score__mutmut_72': x_calculate_score__mutmut_72, 
    'x_calculate_score__mutmut_73': x_calculate_score__mutmut_73, 
    'x_calculate_score__mutmut_74': x_calculate_score__mutmut_74, 
    'x_calculate_score__mutmut_75': x_calculate_score__mutmut_75, 
    'x_calculate_score__mutmut_76': x_calculate_score__mutmut_76, 
    'x_calculate_score__mutmut_77': x_calculate_score__mutmut_77, 
    'x_calculate_score__mutmut_78': x_calculate_score__mutmut_78, 
    'x_calculate_score__mutmut_79': x_calculate_score__mutmut_79, 
    'x_calculate_score__mutmut_80': x_calculate_score__mutmut_80, 
    'x_calculate_score__mutmut_81': x_calculate_score__mutmut_81, 
    'x_calculate_score__mutmut_82': x_calculate_score__mutmut_82, 
    'x_calculate_score__mutmut_83': x_calculate_score__mutmut_83, 
    'x_calculate_score__mutmut_84': x_calculate_score__mutmut_84, 
    'x_calculate_score__mutmut_85': x_calculate_score__mutmut_85, 
    'x_calculate_score__mutmut_86': x_calculate_score__mutmut_86, 
    'x_calculate_score__mutmut_87': x_calculate_score__mutmut_87, 
    'x_calculate_score__mutmut_88': x_calculate_score__mutmut_88, 
    'x_calculate_score__mutmut_89': x_calculate_score__mutmut_89, 
    'x_calculate_score__mutmut_90': x_calculate_score__mutmut_90, 
    'x_calculate_score__mutmut_91': x_calculate_score__mutmut_91, 
    'x_calculate_score__mutmut_92': x_calculate_score__mutmut_92, 
    'x_calculate_score__mutmut_93': x_calculate_score__mutmut_93, 
    'x_calculate_score__mutmut_94': x_calculate_score__mutmut_94, 
    'x_calculate_score__mutmut_95': x_calculate_score__mutmut_95, 
    'x_calculate_score__mutmut_96': x_calculate_score__mutmut_96, 
    'x_calculate_score__mutmut_97': x_calculate_score__mutmut_97, 
    'x_calculate_score__mutmut_98': x_calculate_score__mutmut_98, 
    'x_calculate_score__mutmut_99': x_calculate_score__mutmut_99, 
    'x_calculate_score__mutmut_100': x_calculate_score__mutmut_100, 
    'x_calculate_score__mutmut_101': x_calculate_score__mutmut_101, 
    'x_calculate_score__mutmut_102': x_calculate_score__mutmut_102, 
    'x_calculate_score__mutmut_103': x_calculate_score__mutmut_103, 
    'x_calculate_score__mutmut_104': x_calculate_score__mutmut_104, 
    'x_calculate_score__mutmut_105': x_calculate_score__mutmut_105, 
    'x_calculate_score__mutmut_106': x_calculate_score__mutmut_106, 
    'x_calculate_score__mutmut_107': x_calculate_score__mutmut_107, 
    'x_calculate_score__mutmut_108': x_calculate_score__mutmut_108, 
    'x_calculate_score__mutmut_109': x_calculate_score__mutmut_109, 
    'x_calculate_score__mutmut_110': x_calculate_score__mutmut_110, 
    'x_calculate_score__mutmut_111': x_calculate_score__mutmut_111, 
    'x_calculate_score__mutmut_112': x_calculate_score__mutmut_112, 
    'x_calculate_score__mutmut_113': x_calculate_score__mutmut_113, 
    'x_calculate_score__mutmut_114': x_calculate_score__mutmut_114, 
    'x_calculate_score__mutmut_115': x_calculate_score__mutmut_115, 
    'x_calculate_score__mutmut_116': x_calculate_score__mutmut_116, 
    'x_calculate_score__mutmut_117': x_calculate_score__mutmut_117, 
    'x_calculate_score__mutmut_118': x_calculate_score__mutmut_118, 
    'x_calculate_score__mutmut_119': x_calculate_score__mutmut_119, 
    'x_calculate_score__mutmut_120': x_calculate_score__mutmut_120, 
    'x_calculate_score__mutmut_121': x_calculate_score__mutmut_121, 
    'x_calculate_score__mutmut_122': x_calculate_score__mutmut_122, 
    'x_calculate_score__mutmut_123': x_calculate_score__mutmut_123, 
    'x_calculate_score__mutmut_124': x_calculate_score__mutmut_124, 
    'x_calculate_score__mutmut_125': x_calculate_score__mutmut_125, 
    'x_calculate_score__mutmut_126': x_calculate_score__mutmut_126, 
    'x_calculate_score__mutmut_127': x_calculate_score__mutmut_127, 
    'x_calculate_score__mutmut_128': x_calculate_score__mutmut_128, 
    'x_calculate_score__mutmut_129': x_calculate_score__mutmut_129, 
    'x_calculate_score__mutmut_130': x_calculate_score__mutmut_130
}
x_calculate_score__mutmut_orig.__name__ = 'x_calculate_score'


def score_mcq_locally(
    questions: List[QuestionSubmission],
    max_xp: int,
) -> dict:
    args = [questions, max_xp]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_score_mcq_locally__mutmut_orig, x_score_mcq_locally__mutmut_mutants, args, kwargs, None)


def x_score_mcq_locally__mutmut_orig(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_1(
    questions: List[QuestionSubmission],
    max_xp: int,
) -> dict:
    """
    Score multiple-choice and true/false questions locally (no Groq needed).
    user_answer = index (int or str); correct_answer = index (int or str).
    """
    if questions:
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_2(
    questions: List[QuestionSubmission],
    max_xp: int,
) -> dict:
    """
    Score multiple-choice and true/false questions locally (no Groq needed).
    user_answer = index (int or str); correct_answer = index (int or str).
    """
    if not questions:
        return {
            "XXtotal_scoreXX": 0,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_3(
    questions: List[QuestionSubmission],
    max_xp: int,
) -> dict:
    """
    Score multiple-choice and true/false questions locally (no Groq needed).
    user_answer = index (int or str); correct_answer = index (int or str).
    """
    if not questions:
        return {
            "TOTAL_SCORE": 0,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_4(
    questions: List[QuestionSubmission],
    max_xp: int,
) -> dict:
    """
    Score multiple-choice and true/false questions locally (no Groq needed).
    user_answer = index (int or str); correct_answer = index (int or str).
    """
    if not questions:
        return {
            "total_score": 1,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_5(
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
            "XXpercentageXX": 0.0,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_6(
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
            "PERCENTAGE": 0.0,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_7(
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
            "percentage": 1.0,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_8(
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
            "XXpassedXX": False,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_9(
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
            "PASSED": False,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_10(
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
            "passed": True,
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_11(
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
            "XXquestion_resultsXX": [],
        }

    per_question_xp = round(max_xp / len(questions))
    groq_scores = []

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_12(
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
            "QUESTION_RESULTS": [],
        }

    per_question_xp = round(max_xp / len(questions))
    groq_scores = []

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_13(
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

    per_question_xp = None
    groq_scores = []

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_14(
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

    per_question_xp = round(None)
    groq_scores = []

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_15(
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

    per_question_xp = round(max_xp * len(questions))
    groq_scores = []

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_16(
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
    groq_scores = None

    for q in questions:
        correct = (str(q.user_answer).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_17(
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
        correct = None
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_18(
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
        correct = (str(None).strip() == str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_19(
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
        correct = (str(q.user_answer).strip() != str(q.correct_answer).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_20(
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
        correct = (str(q.user_answer).strip() == str(None).strip())
        groq_scores.append({
            "question_id": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_21(
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
        groq_scores.append(None)

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_22(
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
            "XXquestion_idXX": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_23(
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
            "QUESTION_ID": q.question_id,
            "score": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_24(
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
            "XXscoreXX": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_25(
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
            "SCORE": per_question_xp if correct else 0,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_26(
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
            "score": per_question_xp if correct else 1,
            "correct": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_27(
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
            "XXcorrectXX": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_28(
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
            "CORRECT": correct,
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_29(
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
            "XXfeedbackXX": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_30(
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
            "FEEDBACK": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_31(
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
            "feedback": (
                "XXCorrect!XX" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_32(
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
            "feedback": (
                "correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_33(
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
            "feedback": (
                "CORRECT!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_34(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(None, max_xp, groq_scores)


def x_score_mcq_locally__mutmut_35(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, None, groq_scores)


def x_score_mcq_locally__mutmut_36(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, None)


def x_score_mcq_locally__mutmut_37(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(max_xp, groq_scores)


def x_score_mcq_locally__mutmut_38(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, groq_scores)


def x_score_mcq_locally__mutmut_39(
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
            "feedback": (
                "Correct!" if correct
                else f"The correct answer was option {q.correct_answer}."
            ),
        })

    return calculate_score(questions, max_xp, )

x_score_mcq_locally__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_score_mcq_locally__mutmut_1': x_score_mcq_locally__mutmut_1, 
    'x_score_mcq_locally__mutmut_2': x_score_mcq_locally__mutmut_2, 
    'x_score_mcq_locally__mutmut_3': x_score_mcq_locally__mutmut_3, 
    'x_score_mcq_locally__mutmut_4': x_score_mcq_locally__mutmut_4, 
    'x_score_mcq_locally__mutmut_5': x_score_mcq_locally__mutmut_5, 
    'x_score_mcq_locally__mutmut_6': x_score_mcq_locally__mutmut_6, 
    'x_score_mcq_locally__mutmut_7': x_score_mcq_locally__mutmut_7, 
    'x_score_mcq_locally__mutmut_8': x_score_mcq_locally__mutmut_8, 
    'x_score_mcq_locally__mutmut_9': x_score_mcq_locally__mutmut_9, 
    'x_score_mcq_locally__mutmut_10': x_score_mcq_locally__mutmut_10, 
    'x_score_mcq_locally__mutmut_11': x_score_mcq_locally__mutmut_11, 
    'x_score_mcq_locally__mutmut_12': x_score_mcq_locally__mutmut_12, 
    'x_score_mcq_locally__mutmut_13': x_score_mcq_locally__mutmut_13, 
    'x_score_mcq_locally__mutmut_14': x_score_mcq_locally__mutmut_14, 
    'x_score_mcq_locally__mutmut_15': x_score_mcq_locally__mutmut_15, 
    'x_score_mcq_locally__mutmut_16': x_score_mcq_locally__mutmut_16, 
    'x_score_mcq_locally__mutmut_17': x_score_mcq_locally__mutmut_17, 
    'x_score_mcq_locally__mutmut_18': x_score_mcq_locally__mutmut_18, 
    'x_score_mcq_locally__mutmut_19': x_score_mcq_locally__mutmut_19, 
    'x_score_mcq_locally__mutmut_20': x_score_mcq_locally__mutmut_20, 
    'x_score_mcq_locally__mutmut_21': x_score_mcq_locally__mutmut_21, 
    'x_score_mcq_locally__mutmut_22': x_score_mcq_locally__mutmut_22, 
    'x_score_mcq_locally__mutmut_23': x_score_mcq_locally__mutmut_23, 
    'x_score_mcq_locally__mutmut_24': x_score_mcq_locally__mutmut_24, 
    'x_score_mcq_locally__mutmut_25': x_score_mcq_locally__mutmut_25, 
    'x_score_mcq_locally__mutmut_26': x_score_mcq_locally__mutmut_26, 
    'x_score_mcq_locally__mutmut_27': x_score_mcq_locally__mutmut_27, 
    'x_score_mcq_locally__mutmut_28': x_score_mcq_locally__mutmut_28, 
    'x_score_mcq_locally__mutmut_29': x_score_mcq_locally__mutmut_29, 
    'x_score_mcq_locally__mutmut_30': x_score_mcq_locally__mutmut_30, 
    'x_score_mcq_locally__mutmut_31': x_score_mcq_locally__mutmut_31, 
    'x_score_mcq_locally__mutmut_32': x_score_mcq_locally__mutmut_32, 
    'x_score_mcq_locally__mutmut_33': x_score_mcq_locally__mutmut_33, 
    'x_score_mcq_locally__mutmut_34': x_score_mcq_locally__mutmut_34, 
    'x_score_mcq_locally__mutmut_35': x_score_mcq_locally__mutmut_35, 
    'x_score_mcq_locally__mutmut_36': x_score_mcq_locally__mutmut_36, 
    'x_score_mcq_locally__mutmut_37': x_score_mcq_locally__mutmut_37, 
    'x_score_mcq_locally__mutmut_38': x_score_mcq_locally__mutmut_38, 
    'x_score_mcq_locally__mutmut_39': x_score_mcq_locally__mutmut_39
}
x_score_mcq_locally__mutmut_orig.__name__ = 'x_score_mcq_locally'
