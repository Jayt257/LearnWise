"""
backend/app/services/groq_service.py
Groq API integration for activity answer validation.
Uses llama3-8b-8192 to evaluate user answers and return structured JSON scores.
Handles all 8 activity types with tailored prompts.

Bug Fixes:
  #3: Robust JSON extraction — handles all code fence variants
  #14: Per-question score clamping to [0, per_q_max]
New Features:
  - feedback_tier parameter drives tier-specific Groq prompts
  - (hint | lesson | praise) based on score + attempt_count
"""

import json
import re
import logging
from typing import List, Any
from groq import Groq
from app.core.config import settings
from app.schemas.activity import QuestionSubmission

logger = logging.getLogger(__name__)

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


SYSTEM_PROMPT = """You are LearnWise, an expert language learning evaluator.
You evaluate student answers fairly and provide constructive feedback.
You MUST respond ONLY with valid JSON — no markdown, no extra text, no code fences.
Be encouraging but honest. Give partial credit where deserved."""


def _determine_feedback_tier(percentage: float, attempt_count: int) -> str:
    """
    Determine which feedback tier to apply based on score and attempts.
      - hint:   score < 50% AND repeated attempts (≥2) — actionable next-try hints
      - lesson: score 50–79% — brief lesson on the concept
      - praise: score ≥ 80% — celebration + advanced tip
    """
    if percentage >= 80.0:
        return "praise"
    elif percentage >= 50.0:
        return "lesson"
    else:
        return "hint" if attempt_count >= 2 else "lesson"


_TIER_INSTRUCTIONS = {
    "hint": (
        "The student has failed this activity multiple times. "
        "In 'overall_feedback', give 2–3 very specific hints about what they got wrong and how to fix it. "
        "Be empathetic and encouraging. Keep it under 60 words. "
        "In 'suggestion', give ONE concrete next step they can take right now."
    ),
    "lesson": (
        "The student scored in the moderate range. "
        "In 'overall_feedback', write a brief 2–3 sentence mini-lesson explaining the key concept "
        "they need to improve. Use a friendly, teacher-like tone. Keep it under 80 words. "
        "In 'suggestion', suggest one specific practice exercise."
    ),
    "praise": (
        "The student did very well! "
        "In 'overall_feedback', celebrate their success warmly and note what they did right. Keep under 50 words. "
        "In 'suggestion', give one advanced tip to push towards mastery — something beyond the basics."
    ),
}


def _build_prompt(
    activity_type: str,
    questions: List[QuestionSubmission],
    max_xp: int,
    user_lang: str,
    target_lang: str,
    feedback_tier: str = "lesson",
) -> str:
    """Build the evaluation prompt for Groq based on activity type and feedback tier."""

    questions_text = []
    for i, q in enumerate(questions):
        entry = f"Question {i+1} (id={q.question_id}, type={q.block_type}):\n"
        if q.prompt:
            entry += f"  Prompt: {q.prompt}\n"
        if q.correct_answer is not None:
            entry += f"  Correct answer: {q.correct_answer}\n"
        if q.sample_answer:
            entry += f"  Sample/expected answer: {q.sample_answer}\n"
        user_ans = str(q.user_answer)[:500] if q.user_answer else "(no answer)"
        entry += f"  Student's answer: {user_ans}\n"
        questions_text.append(entry)

    questions_block = "\n".join(questions_text)
    num_questions = len(questions)
    per_q_max = round(max_xp / num_questions) if num_questions else max_xp

    activity_instructions = {
        "lesson": "Evaluate fill-in-the-blank and reading comprehension answers. Full credit for correct answers.",
        "vocab": "Evaluate vocabulary answers: translations, matching, and usage. Award partial credit for close answers.",
        "reading": "Evaluate reading comprehension: MCQ, true/false, gap-fill. Be strict on factual accuracy.",
        "writing": "Evaluate free-writing and translation tasks. Score on: accuracy of meaning, grammar, and vocabulary use. Award generous partial credit.",
        "listening": "Evaluate listening comprehension: gap-fill and true/false based on the transcript. Be fair.",
        "speaking": "The student's speech was transcribed by Whisper (may have minor errors). Evaluate scenario performance: did they convey the right meaning? Award partial credit for good attempts.",
        "pronunciation": "The student's speech was transcribed by Whisper. Compare the transcribed text to the target. Award credit based on how close the pronunciation was (minor Whisper errors are expected).",
        "test": "This is a formal test. Score strictly. Only award full marks for clearly correct answers.",
    }

    instruction = activity_instructions.get(activity_type, "Evaluate the student's answer fairly.")
    tier_instruction = _TIER_INSTRUCTIONS.get(feedback_tier, _TIER_INSTRUCTIONS["lesson"])

    prompt = f"""Activity Type: {activity_type}
Native Language: {user_lang} | Learning: {target_lang}
Total Max XP: {max_xp} | Per-question max: {per_q_max} XP
Number of questions: {num_questions}

Evaluation Instructions: {instruction}

Feedback Style ({feedback_tier.upper()} tier): {tier_instruction}

--- STUDENT ANSWERS ---
{questions_block}

Respond with ONLY this exact JSON (no markdown, no code fences):
{{
  "question_results": [
    {{
      "question_id": "<id>",
      "score": <integer 0 to {per_q_max}>,
      "correct": <true|false>,
      "feedback": "<brief specific feedback>"
    }}
  ],
  "overall_feedback": "<feedback per the {feedback_tier} tier instructions above>",
  "suggestion": "<1 specific improvement tip>"
}}"""

    return prompt


def _extract_json(raw: str) -> dict:
    """
    Robustly extract JSON from Groq response.
    Handles: plain JSON, ```json...```, ```...```, leading/trailing whitespace,
    and JSON embedded in explanatory text.

    Bug Fix #3: Previous code only handled one code fence pattern.
    """
    raw = raw.strip()

    # Pattern 1: Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
    match = fence_pattern.search(raw)
    if match:
        raw = match.group(1).strip()

    # Pattern 2: Find first { ... } JSON object in the string
    # This handles cases where Groq adds explanatory text before/after JSON
    brace_match = re.search(r"\{[\s\S]*\}", raw)
    if brace_match:
        raw = brace_match.group(0)

    return json.loads(raw)


def _clamp_scores(question_results: list, per_q_max: int) -> list:
    """
    Bug Fix #14: Clamp each per-question score to [0, per_q_max].
    Groq sometimes returns scores > max — this prevents total > max_xp.
    """
    clamped = []
    for q in question_results:
        score = q.get("score", 0)
        if not isinstance(score, (int, float)):
            score = 0
        score = max(0, min(int(score), per_q_max))
        clamped.append({**q, "score": score})
    return clamped


def validate_activity(
    activity_type: str,
    questions: List[QuestionSubmission],
    max_xp: int,
    user_lang: str = "hi",
    target_lang: str = "en",
    attempt_count: int = 1,
) -> dict:
    """
    Send activity answers to Groq for evaluation.
    Returns parsed dict with question_results, overall_feedback, suggestion, feedback_tier.
    Falls back to local scoring on API errors.
    """
    num_questions = len(questions)
    per_q_max = round(max_xp / num_questions) if num_questions else max_xp

    # Determine feedback tier upfront (we don't know score yet — we'll recalculate after)
    # Use a preliminary estimate: for now pass "lesson" to Groq, then patch tier after scoring
    feedback_tier = "lesson"  # Will be corrected in validate router after score is known

    try:
        client = get_client()
        prompt = _build_prompt(
            activity_type, questions, max_xp, user_lang, target_lang, feedback_tier
        )

        # Estimate token count to decide max_tokens
        estimated_input_tokens = len(prompt) // 4
        max_tokens = min(2000, max(800, num_questions * 120))

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()
        logger.info(f"[GROQ RAW] {raw[:800]}")
        result = _extract_json(raw)
        logger.info(f"[GROQ PARSED] question_results={result.get('question_results')} per_q_max={per_q_max}")

        # Clamp scores (Bug Fix #14)
        if "question_results" in result:
            result["question_results"] = _clamp_scores(result["question_results"], per_q_max)
        logger.info(f"[GROQ CLAMPED] {result.get('question_results')}")

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Groq returned invalid JSON: {e}")
        return _fallback_result(questions, max_xp)
    except Exception as e:
        logger.error(f"Groq API error: {type(e).__name__}: {e}")
        return _fallback_result(questions, max_xp)


def generate_tier_feedback(
    activity_type: str,
    feedback_tier: str,
    overall_feedback: str,
    suggestion: str,
    user_lang: str,
    target_lang: str,
) -> dict:
    """
    Optional: Re-call Groq specifically to generate tier-appropriate feedback.
    Used when the scoring already happened but feedback needs to be refined for tier.
    Returns updated {overall_feedback, suggestion}.
    """
    try:
        client = get_client()
        tier_instruction = _TIER_INSTRUCTIONS.get(feedback_tier, _TIER_INSTRUCTIONS["lesson"])
        prompt = f"""A language learner just completed a '{activity_type}' activity.
Native language: {user_lang}, learning: {target_lang}.
Feedback tier: {feedback_tier.upper()}

Original feedback: {overall_feedback}
Original suggestion: {suggestion}

Rewrite the feedback following this style: {tier_instruction}

Respond with ONLY:
{{"overall_feedback": "<rewritten>", "suggestion": "<rewritten>"}}"""

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        return _extract_json(raw)
    except Exception as e:
        logger.error(f"Tier feedback generation failed: {e}")
        return {"overall_feedback": overall_feedback, "suggestion": suggestion}


def _fallback_result(questions: List[QuestionSubmission], max_xp: int) -> dict:
    """Local fallback scoring when Groq is unavailable."""
    per_q = round(max_xp / len(questions)) if questions else 0
    results = []
    for q in questions:
        user_ans = str(q.user_answer).strip().lower() if q.user_answer else ""
        correct_ans = str(q.correct_answer).strip().lower() if q.correct_answer else ""
        correct = bool(user_ans and user_ans == correct_ans)
        results.append({
            "question_id": q.question_id,
            "score": per_q if correct else round(per_q * 0.3),
            "correct": correct,
            "feedback": "Correct!" if correct else "Good try! Keep practicing.",
        })
    return {
        "question_results": results,
        "overall_feedback": "Activity evaluated locally (AI unavailable). Keep practicing to improve!",
        "suggestion": "Review the lesson materials and try again for a better score.",
    }
