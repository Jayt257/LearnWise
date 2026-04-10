"""
backend/app/routers/admin.py
Admin-only endpoints (require role=admin).
  GET    /api/admin/stats
  GET    /api/admin/users
  PUT    /api/admin/users/{user_id}/role
  PUT    /api/admin/users/{user_id}/activate
  DELETE /api/admin/users/{user_id}
  GET    /api/admin/languages
  POST   /api/admin/languages
  DELETE /api/admin/languages/{pair_id}
  GET    /api/admin/content/{pair_id}
  GET    /api/admin/content/{pair_id}/file
  PUT    /api/admin/content/{pair_id}
  PUT    /api/admin/content/{pair_id}/meta
  POST   /api/admin/content/{pair_id}/activity
  DELETE /api/admin/content/{pair_id}/activity
  POST   /api/admin/content/{pair_id}/month       [NEW] Add a new month
  POST   /api/admin/content/{pair_id}/month/{month}/block  [NEW] Add a new block
  GET    /api/admin/analytics
  GET    /api/admin/activity-types
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from datetime import datetime, timedelta
from uuid import UUID
from typing import List, Optional
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User, UserRole
from app.models.progress import UserLanguageProgress, ActivityCompletion
from app.schemas.admin import (
    AdminUserOut, UpdateUserRoleRequest, PlatformStats,
    CreateLanguagePairRequest, UpdateContentRequest
)
from app.services import content_service

router = APIRouter(prefix="/admin", tags=["Admin"])

# Supported activity types matching data_README section 5
ACTIVITY_TYPES = {
    "lesson": {
        "label": "Lesson",
        "icon": "📖",
        "description": "Teach the main concept, grammar rule, or cultural point",
        "file_name": "lesson.json",
    },
    "pronunciation": {
        "label": "Pronunciation",
        "icon": "🗣",
        "description": "Correct audio, phonetic guidance, user speech check, score",
        "file_name": "pronunciation.json",
    },
    "reading": {
        "label": "Reading",
        "icon": "📄",
        "description": "Reading passage with native-language support, glossary, comprehension questions",
        "file_name": "reading.json",
    },
    "writing": {
        "label": "Writing",
        "icon": "✍",
        "description": "Writing prompt with hints, rubric, and scoring",
        "file_name": "writing.json",
    },
    "listening": {
        "label": "Listening",
        "icon": "🎧",
        "description": "Audio clip with transcript, questions, and answer evaluation",
        "file_name": "listening.json",
    },
    "vocabulary": {
        "label": "Vocabulary",
        "icon": "📝",
        "description": "Word groups with meanings, usage examples, audio support, and quizzes",
        "file_name": "vocabulary.json",
    },
    "speaking": {
        "label": "Speaking",
        "icon": "🎙",
        "description": "Scenario-based speaking task with time limit and scoring",
        "file_name": "speaking.json",
    },
    "test": {
        "label": "Test",
        "icon": "📋",
        "description": "End-of-block evaluation covering all skill areas",
        "file_name": "test.json",
    },
}

# Minimal JSON templates per data_README schemas
def _make_template(activity_type: str, pair_id: str = "hi-ja", month: int = 1, block: int = 1) -> dict:
    """Generate a minimal valid activity template matching data_README schema."""
    src, tgt = pair_id.split("-") if "-" in pair_id else ("hi", "ja")
    block_code = f"M{month}B{block}"
    activity_id = f"{tgt}_{src}_{block_code}_{activity_type}_001"

    base = {
        "activityId": activity_id,
        "monthNumber": month,
        "blockNumber": block,
        "activityType": activity_type,
        "title": f"New {activity_type.capitalize()} — {block_code}",
        "learningGoal": "The learner will be able to [describe goal here].",
        "difficultyLevel": "beginner",
        "baseLanguage": src,
        "targetLanguage": tgt,
        "estimatedTime": 30,
        "prerequisites": [],
        "instructions": "Instructions for this activity go here.",
        "contentItems": [],
        "adminCorrectAnswerSet": {},
        "evaluationMode": "exact_match",
        "scoreThreshold": 70,
        "feedbackRules": {
            "onPass": "Well done!",
            "onFail": "Please review and try again.",
            "onPartial": "Good effort! Review missed areas."
        },
        "audioAssets": {
            "promptAudio": None,
            "nativeAudio": None,
            "referenceAudio": None,
            "instructionAudio": None,
            "sampleAudio": None,
            "slowAudio": None,
            "normalAudio": None,
            "audioTranscript": None,
            "audioLanguage": tgt,
            "audioDuration": None,
            "audioRepeatAllowed": True
        },
        "tags": [activity_type, f"month{month}", f"block{block}"],
        "status": "draft",
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "thumbnail": None,
        "imageAssets": [],
        "videoAssets": [],
        "hintText": None,
        "commonMistakes": [],
        "reviewLinks": [],
        "nextActivityIds": [],
        "attemptLimit": None,
        "metadata": {}
    }

    # Add activity-type specific fields
    if activity_type == "lesson":
        base.update({
            "conceptTitle": "Concept title here",
            "lessonContent": [
                {
                    "sectionId": "sec_1",
                    "sectionTitle": "Introduction",
                    "bodyText": "Detailed explanation goes here.",
                    "targetLanguageExamples": []
                }
            ],
            "learningObjective": "Measurable objective here.",
            "examples": [],
            "importantRules": [],
            "cultureContext": {"isApplicable": False, "contextText": None, "dosList": [], "dontsList": []},
            "summary": "Summary of key points.",
            "checkpointQuestions": [],
            "adminCorrectAnswerSet": {
                "keyTakeaways": [],
                "conceptSummary": "",
                "importantFacts": [],
                "checkpointAnswers": {},
                "expectedUnderstanding": ""
            }
        })
    elif activity_type == "pronunciation":
        base.update({
            "targetPhrasesOrWords": [],
            "userInputMode": "speech",
            "sttTranscript": None,
            "expectedPronunciationText": "",
            "adminCorrectAnswerSet": {
                "exactCorrectTranscript": "",
                "acceptedVariants": [],
                "syllableSplitReference": "",
                "phoneticApproximation": "",
                "nativeScriptReference": None,
                "transliteration": None,
                "strictnessLevel": "moderate"
            }
        })
    elif activity_type == "reading":
        base.update({
            "readingTitle": "Reading passage title",
            "readingText": "",
            "textInTargetLanguage": "",
            "baseLanguageSupportText": None,
            "glossary": [],
            "sentenceSupportPairs": [],
            "comprehensionQuestions": [],
            "readAloudMode": False,
            "adminCorrectAnswerSet": {
                "correctAnswers": {},
                "acceptableParaphrases": {},
                "keywordScoringRules": {},
                "expectedSummaryPoints": []
            }
        })
    elif activity_type == "writing":
        base.update({
            "writingPrompt": "Writing prompt here.",
            "promptGoal": "Goal of writing task.",
            "expectedWritingType": "paragraph",
            "wordBank": [],
            "referenceHints": [],
            "modelExampleOutputs": [],
            "evaluationCriteria": [
                {"criterion": "Grammar Accuracy", "weight": 40, "description": "Correct grammar usage"},
                {"criterion": "Content Coverage", "weight": 40, "description": "Covers required topics"},
                {"criterion": "Vocabulary", "weight": 20, "description": "Appropriate word choice"}
            ],
            "minimumWordCount": 50,
            "maximumWordCount": 150,
            "adminCorrectAnswerSet": {
                "sampleAnswer": "",
                "acceptableAlternates": [],
                "requiredKeywords": [],
                "grammarBaseline": "",
                "lengthExpectation": "50 to 150 words",
                "scoringRubric": {}
            }
        })
    elif activity_type == "listening":
        base.update({
            "listeningGoal": "Extract information from the audio.",
            "audioScenario": "Description of audio context.",
            "audioTranscriptSentences": [],
            "audioTranscriptFull": "",
            "questionSet": [],
            "replayAllowed": True,
            "slowPlaybackAllowed": True,
            "scoringRules": {
                "pointsPerQuestion": 10,
                "partialCreditAllowed": True,
                "partialCreditRules": None
            },
            "adminCorrectAnswerSet": {
                "correctAnswers": {},
                "acceptedShortAnswers": {},
                "acceptedLongAnswers": {},
                "scoringKeywords": {},
                "partialCreditRules": {}
            }
        })
    elif activity_type == "vocabulary":
        base.update({
            "vocabTheme": "Vocabulary theme here",
            "wordList": [],
            "meaningList": [],
            "exampleSentences": [],
            "quizType": "mixed",
            "quizQuestions": [],
            "adminCorrectAnswerSet": {
                "correctMeanings": {},
                "acceptedTranslations": {},
                "matchingKey": {},
                "mcqAnswerKey": {},
                "pronunciationReference": {}
            }
        })
    elif activity_type == "speaking":
        base.update({
            "speakingPrompt": "Speaking task instruction here.",
            "scenario": "Full scenario description here.",
            "role": "learner",
            "conversationPartner": None,
            "subTasks": [],
            "scenarioContext": {
                "targetText": "",
                "transliteration": "",
                "baseTranslation": ""
            },
            "baselineTranscriptSentences": [],
            "scoringRules": {
                "fluencyWeight": 25,
                "contentWeight": 40,
                "grammarWeight": 20,
                "vocabularyWeight": 15
            },
            "adminCorrectAnswerSet": {
                "expectedSpeakingPoints": [],
                "requiredKeywords": [],
                "acceptableParaphrases": [],
                "scoringRubric": {},
                "sampleAnswer": "",
                "minimumContentCoverage": 60
            }
        })
    elif activity_type == "test":
        base.update({
            "testTitle": "Block Test",
            "testScope": "block_test",
            "coveredActivityTypes": ["lesson", "vocabulary", "pronunciation", "listening"],
            "testInstructions": "Answer all questions carefully.",
            "questionSections": [],
            "scoreWeights": {
                "lesson": 15, "pronunciation": 10, "reading": 15,
                "writing": 15, "listening": 15, "vocabulary": 15, "speaking": 15
            },
            "totalMarks": 100,
            "passMarks": 70,
            "userResponses": {},
            "finalScore": None,
            "sectionScores": {},
            "resultSummary": None,
            "adminCorrectAnswerSet": {
                "answerKey": {},
                "scoringRubric": {},
                "partialCreditRules": {},
                "alternateValidAnswers": {},
                "sectionPassMarks": {}
            }
        })

    return base


# ── Stats ──────────────────────────────────────────────────────

@router.get("/stats", response_model=PlatformStats)
def get_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).filter(User.role == UserRole.user).scalar()
    yesterday = datetime.utcnow() - timedelta(hours=24)
    active_today = db.query(func.count(User.id)).filter(User.last_active >= yesterday).scalar()
    total_completions = db.query(func.count(ActivityCompletion.id)).scalar()
    total_xp = db.query(func.sum(ActivityCompletion.score_earned)).scalar() or 0
    pairs = content_service.get_all_pairs()

    top_pair = db.query(
        UserLanguageProgress.lang_pair_id,
        func.count(UserLanguageProgress.id).label("cnt")
    ).group_by(UserLanguageProgress.lang_pair_id).order_by(func.count(UserLanguageProgress.id).desc()).first()

    return PlatformStats(
        total_users=total_users or 0,
        active_today=active_today or 0,
        total_completions=total_completions or 0,
        total_xp_awarded=int(total_xp),
        language_pairs=len(pairs),
        top_language_pair=top_pair[0] if top_pair else None,
    )


# ── Analytics ────────────────────────────────────────────────

@router.get("/analytics")
def get_analytics(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Per-activity-type analytics: completion count, avg score, pass rate."""
    activity_stats_raw = db.query(
        ActivityCompletion.activity_type,
        func.count(ActivityCompletion.id).label("total"),
        func.avg(ActivityCompletion.score_earned).label("avg_score"),
        func.sum(func.cast(ActivityCompletion.passed, Integer)).label("passed_count"),
    ).group_by(ActivityCompletion.activity_type).all()

    activity_stats = []
    for row in activity_stats_raw:
        total = row.total or 0
        passed = int(row.passed_count or 0)
        activity_stats.append({
            "activity_type": row.activity_type,
            "total_completions": total,
            "avg_score": round(float(row.avg_score or 0), 1),
            "pass_rate": round((passed / total * 100) if total > 0 else 0, 1),
        })

    top_users_raw = db.query(
        User.username,
        User.display_name,
        func.sum(UserLanguageProgress.total_xp).label("total_xp"),
    ).join(UserLanguageProgress, User.id == UserLanguageProgress.user_id
    ).group_by(User.id, User.username, User.display_name
    ).order_by(func.sum(UserLanguageProgress.total_xp).desc()
    ).limit(5).all()

    top_users = [
        {"username": u.username, "display_name": u.display_name, "total_xp": int(u.total_xp or 0)}
        for u in top_users_raw
    ]

    recent_raw = db.query(ActivityCompletion).order_by(
        ActivityCompletion.completed_at.desc()
    ).limit(10).all()

    recent_completions = [
        {
            "activity_type": c.activity_type,
            "activity_seq_id": c.activity_seq_id,
            "activity_json_id": c.activity_json_id,
            "lang_pair_id": c.lang_pair_id,
            "month_number": c.month_number,
            "block_number": c.block_number,
            "score_earned": c.score_earned,
            "max_score": c.max_score,
            "passed": c.passed,
            "completed_at": c.completed_at.isoformat() if c.completed_at else None,
        }
        for c in recent_raw
    ]

    pair_enrollments_raw = db.query(
        UserLanguageProgress.lang_pair_id,
        func.count(UserLanguageProgress.id).label("cnt"),
        func.sum(UserLanguageProgress.total_xp).label("total_xp"),
    ).group_by(UserLanguageProgress.lang_pair_id).all()

    pair_enrollments = [
        {"lang_pair_id": r.lang_pair_id, "enrolled_users": int(r.cnt or 0), "total_xp": int(r.total_xp or 0)}
        for r in pair_enrollments_raw
    ]

    return {
        "activity_stats": activity_stats,
        "top_users": top_users,
        "recent_completions": recent_completions,
        "pair_enrollments": pair_enrollments,
    }


# ── Activity Types ──────────────────────────────────────────

@router.get("/activity-types")
def get_activity_types(admin: User = Depends(require_admin)):
    """Return metadata for all supported activity types + JSON templates."""
    return {
        "activity_types": [
            {**{"id": k}, **v}
            for k, v in ACTIVITY_TYPES.items()
        ],
        "templates": {k: _make_template(k) for k in ACTIVITY_TYPES},
    }


# ── Users ──────────────────────────────────────────────────────

@router.get("/users", response_model=List[AdminUserOut])
def list_users(
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )
    if role and role in ("user", "admin"):
        query = query.filter(User.role == UserRole(role))
    users = query.order_by(User.created_at.desc()).all()
    return [AdminUserOut.model_validate(u) for u in users]


@router.put("/users/{user_id}/role")
def update_role(
    user_id: UUID,
    req: UpdateUserRoleRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        user.role = UserRole(req.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role '{req.role}'. Must be 'user' or 'admin'.")
    db.commit()
    return {"message": f"User role updated to {req.role}"}


@router.delete("/users/{user_id}")
def deactivate_user(user_id: UUID, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user.id) == str(admin.id):
        raise HTTPException(status_code=400, detail="Cannot deactivate your own admin account.")
    user.is_active = False
    db.commit()
    return {"message": "User deactivated successfully"}


@router.put("/users/{user_id}/activate")
def activate_user(user_id: UUID, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        return {"message": "User is already active"}
    user.is_active = True
    db.commit()
    return {"message": f"User '{user.username}' has been reactivated successfully"}


# ── Languages ──────────────────────────────────────────────────

@router.get("/languages")
def list_languages(admin: User = Depends(require_admin)):
    pairs = content_service.get_all_pairs()
    enriched = []
    for p in pairs:
        try:
            meta = content_service.get_meta(p["pairId"])
            enriched.append({**p, "meta": meta})
        except Exception:
            enriched.append({**p, "meta": None})
    return enriched


@router.post("/languages", status_code=201)
def create_language(req: CreateLanguagePairRequest, admin: User = Depends(require_admin)):
    pair_id = f"{req.source_lang_id}-{req.target_lang_id}"

    existing_pairs = content_service.get_all_pairs()
    if any(p["pairId"] == pair_id for p in existing_pairs):
        raise HTTPException(status_code=409, detail=f"Language pair '{pair_id}' already exists.")

    content_service.create_pair_directory(
        pair_id,
        src_id=req.source_lang_id, tgt_id=req.target_lang_id,
        src_name=req.source_lang_name, tgt_name=req.target_lang_name,
        src_flag=req.source_lang_flag, tgt_flag=req.target_lang_flag,
        total_months=3
    )
    content_service.register_pair(pair_id, req.source_lang_id, req.target_lang_id)

    # Build full meta skeleton with 3 months × 6 blocks
    meta = content_service._build_meta_skeleton(
        pair_id,
        src_id=req.source_lang_id, tgt_id=req.target_lang_id,
        src_name=req.source_lang_name, tgt_name=req.target_lang_name,
        src_flag=req.source_lang_flag, tgt_flag=req.target_lang_flag,
        total_months=3, blocks_per_month=6
    )
    content_service.write_meta(pair_id, meta)
    return {"message": f"Language pair '{pair_id}' created successfully", "pair_id": pair_id}


@router.delete("/languages/{pair_id}")
def delete_language(pair_id: str, admin: User = Depends(require_admin)):
    pairs = content_service.get_all_pairs()
    if not any(p["pairId"] == pair_id for p in pairs):
        raise HTTPException(status_code=404, detail=f"Language pair '{pair_id}' not found.")
    content_service.delete_pair(pair_id)
    return {"message": f"Language pair '{pair_id}' deleted successfully"}


# ── Content ────────────────────────────────────────────────────

@router.get("/content/{pair_id}")
def list_content(pair_id: str, admin: User = Depends(require_admin)):
    files = content_service.list_pair_files(pair_id)
    return {"pair_id": pair_id, "files": files, "total": len(files)}


@router.get("/content/{pair_id}/file")
def get_content_file(pair_id: str, file: str, admin: User = Depends(require_admin)):
    try:
        return content_service.get_activity(pair_id, file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file}' not found in pair '{pair_id}'")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Path traversal attempt blocked")


@router.put("/content/{pair_id}")
def update_content(pair_id: str, req: UpdateContentRequest, admin: User = Depends(require_admin)):
    try:
        content_service.write_activity(pair_id, req.file_path, req.content)
        return {"message": f"File '{req.file_path}' updated successfully"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Path traversal attempt blocked")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/content/{pair_id}/meta")
def update_meta(pair_id: str, req: UpdateContentRequest, admin: User = Depends(require_admin)):
    try:
        content_service.write_meta(pair_id, req.content)
        return {"message": "meta.json updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/{pair_id}/activity", status_code=201)
def add_activity(pair_id: str, req: UpdateContentRequest, admin: User = Depends(require_admin)):
    """
    Add a new activity JSON file.
    Raises 409 if the file already exists.
    """
    try:
        base = content_service._base_path(pair_id)
        file_path = base / req.file_path
        file_path.resolve().relative_to(base.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Path traversal attempt blocked")
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid pair_id: {pair_id}")

    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Activity file '{req.file_path}' already exists. Use PUT to update.",
        )
    try:
        content_service.write_activity(pair_id, req.file_path, req.content)
        return {"message": f"Activity '{req.file_path}' created successfully", "file_path": req.file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/content/{pair_id}/activity")
def delete_activity(
    pair_id: str,
    file: str = Query(..., description="Relative file path e.g. month_1/block_1/lesson.json"),
    admin: User = Depends(require_admin),
):
    """Delete a specific activity file from a language pair."""
    try:
        base = content_service._base_path(pair_id)
        file_path = base / file
        file_path.resolve().relative_to(base.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Path traversal attempt blocked")
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid pair_id: {pair_id}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{file}' not found")
    if file_path.name == "meta.json":
        raise HTTPException(status_code=400, detail="Cannot delete meta.json. Use PUT to update it.")

    file_path.unlink()
    return {"message": f"Activity file '{file}' deleted successfully"}


@router.post("/content/{pair_id}/month", status_code=201)
def add_month(pair_id: str, admin: User = Depends(require_admin)):
    """Add a new month (with 6 blocks) to an existing language pair. Updates meta.json."""
    try:
        meta = content_service.add_month(pair_id)
        return {"message": "New month added successfully", "total_months": meta["totalMonths"]}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Language pair '{pair_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/{pair_id}/month/{month}/block", status_code=201)
def add_block(pair_id: str, month: int, admin: User = Depends(require_admin)):
    """Add a new block to an existing month. Updates meta.json."""
    try:
        meta = content_service.add_block(pair_id, month)
        month_data = next((m for m in meta["months"] if m["month"] == month), None)
        return {
            "message": f"New block added to month {month}",
            "total_blocks": len(month_data["blocks"]) if month_data else 0
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Language pair '{pair_id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity-types")
def get_activity_types(admin: User = Depends(require_admin)):
    """Return the list of valid activity types and empty templates for the admin UI."""
    templates = {t: _make_template(t, "hi-ja", 1, 1) for t in ACTIVITY_TYPES}
    return {"types": ACTIVITY_TYPES, "templates": templates}


@router.get("/activity-template/{activity_type}")
def get_activity_template(
    activity_type: str,
    pair_id: str = Query("hi-ja"),
    month: int = Query(1),
    block: int = Query(1),
    admin: User = Depends(require_admin)
):
    """Get a filled JSON template for a specific activity type."""
    if activity_type not in ACTIVITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown activity type: {activity_type}")
    return _make_template(activity_type, pair_id, month, block)


@router.delete("/content/{pair_id}/month/{month}/block/{block}")
def delete_block(pair_id: str, month: int, block: int, admin: User = Depends(require_admin)):
    """Delete an entire block (all its files) and remove it from meta.json."""
    try:
        meta = content_service.get_meta(pair_id)
        month_data = next((m for m in meta["months"] if m["month"] == month), None)
        if not month_data:
            raise HTTPException(status_code=404, detail=f"Month {month} not found")
        block_data = next((b for b in month_data["blocks"] if b["block"] == block), None)
        if not block_data:
            raise HTTPException(status_code=404, detail=f"Block {block} not found in month {month}")

        # Delete all activity files for this block
        base = content_service._base_path(pair_id)
        block_dir = base / f"month_{month}" / f"block_{block}"
        if block_dir.exists():
            import shutil
            shutil.rmtree(block_dir)

        # Remove block from meta
        month_data["blocks"] = [b for b in month_data["blocks"] if b["block"] != block]
        content_service.write_meta(pair_id, meta)
        return {"message": f"Block {block} in month {month} deleted successfully"}
    except (HTTPException):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/content/{pair_id}/month/{month}")
def delete_month(pair_id: str, month: int, admin: User = Depends(require_admin)):
    """Delete an entire month (all its blocks and files) and remove it from meta.json."""
    try:
        meta = content_service.get_meta(pair_id)
        month_data = next((m for m in meta["months"] if m["month"] == month), None)
        if not month_data:
            raise HTTPException(status_code=404, detail=f"Month {month} not found")

        # Delete all block directories for this month
        base = content_service._base_path(pair_id)
        month_dir = base / f"month_{month}"
        if month_dir.exists():
            import shutil
            shutil.rmtree(month_dir)

        # Remove month from meta
        meta["months"] = [m for m in meta["months"] if m["month"] != month]
        meta["totalMonths"] = len(meta["months"])
        content_service.write_meta(pair_id, meta)
        return {"message": f"Month {month} deleted successfully"}
    except (HTTPException):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Inline Meta Editing ────────────────────────────────────────────────────────

from pydantic import BaseModel as _PatchBase
from typing import Optional as _Opt

class PatchMonthRequest(_PatchBase):
    title: _Opt[str] = None
    description: _Opt[str] = None
    target_level: _Opt[str] = None

class PatchBlockRequest(_PatchBase):
    title: _Opt[str] = None


@router.patch("/content/{pair_id}/month/{month}")
def patch_month(pair_id: str, month: int, req: PatchMonthRequest, admin: User = Depends(require_admin)):
    """Update a month's title/description/targetLevel in meta.json."""
    try:
        meta = content_service.get_meta(pair_id)
        month_data = next((m for m in meta["months"] if m["month"] == month), None)
        if not month_data:
            raise HTTPException(status_code=404, detail=f"Month {month} not found")
        if req.title is not None:
            month_data["title"] = req.title
        if req.description is not None:
            month_data["description"] = req.description
        if req.target_level is not None:
            month_data["targetLevel"] = req.target_level
        content_service.write_meta(pair_id, meta)
        return {"message": f"Month {month} updated", "month": month_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/content/{pair_id}/month/{month}/block/{block}")
def patch_block(pair_id: str, month: int, block: int, req: PatchBlockRequest, admin: User = Depends(require_admin)):
    """Update a block's title in meta.json."""
    try:
        meta = content_service.get_meta(pair_id)
        month_data = next((m for m in meta["months"] if m["month"] == month), None)
        if not month_data:
            raise HTTPException(status_code=404, detail=f"Month {month} not found")
        block_data = next((b for b in month_data["blocks"] if b["block"] == block), None)
        if not block_data:
            raise HTTPException(status_code=404, detail=f"Block {block} not found in month {month}")
        if req.title is not None:
            block_data["title"] = req.title
        content_service.write_meta(pair_id, meta)
        return {"message": f"Block {block} updated", "block": block_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
