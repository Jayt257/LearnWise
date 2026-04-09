"""
backend/app/routers/admin.py
Admin-only endpoints (require role=admin).
  GET  /api/admin/stats                         - Platform statistics
  GET  /api/admin/users                         - All users list
  PUT  /api/admin/users/{user_id}/role          - Change user role
  PUT  /api/admin/users/{user_id}/activate      - Reactivate a deactivated user [NEW]
  DELETE /api/admin/users/{user_id}             - Deactivate user
  GET  /api/admin/languages                     - List language pairs
  POST /api/admin/languages                     - Create new language pair
  DELETE /api/admin/languages/{pair_id}         - Delete language pair
  GET  /api/admin/content/{pair_id}             - List content files
  GET  /api/admin/content/{pair_id}/file        - Get a specific content file
  PUT  /api/admin/content/{pair_id}             - Update a content file
  PUT  /api/admin/content/{pair_id}/meta        - Update meta.json
  POST /api/admin/content/{pair_id}/activity    - Add new activity file
  DELETE /api/admin/content/{pair_id}/activity  - Delete an activity file [NEW]
  GET  /api/admin/analytics                     - Per-activity-type analytics [NEW]
  GET  /api/admin/activity-types                - List supported activity types [NEW]
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

# Supported activity types with metadata
ACTIVITY_TYPES = {
    "lesson": {
        "label": "Lesson",
        "icon": "📖",
        "description": "Text, grammar rules, dialogues, and fill-in-the-blank exercises",
        "file_suffix": "lesson",
    },
    "vocab": {
        "label": "Vocabulary",
        "icon": "📝",
        "description": "Word translations, matching, and usage exercises",
        "file_suffix": "vocab",
    },
    "reading": {
        "label": "Reading",
        "icon": "📄",
        "description": "Reading comprehension passages with MCQ and gap-fill",
        "file_suffix": "reading",
    },
    "writing": {
        "label": "Writing",
        "icon": "✍",
        "description": "Translation and free-text composition tasks",
        "file_suffix": "writing",
    },
    "listening": {
        "label": "Listening",
        "icon": "🎧",
        "description": "Audio-based comprehension with gap-fill and true/false",
        "file_suffix": "listening",
    },
    "speaking": {
        "label": "Speaking",
        "icon": "🎙",
        "description": "Scenario roleplay evaluated by Whisper + Groq AI",
        "file_suffix": "speaking",
    },
    "pronunciation": {
        "label": "Pronunciation",
        "icon": "🗣",
        "description": "Read-aloud exercises scored by speech-to-text comparison",
        "file_suffix": "pronunciation",
    },
    "test": {
        "label": "Test",
        "icon": "📋",
        "description": "Formal MCQ test scored locally (no AI needed)",
        "file_suffix": "test",
    },
}

# Minimal JSON templates for each activity type
ACTIVITY_TEMPLATES = {
    "lesson": {
        "title": "New Lesson",
        "description": "Lesson description here",
        "blocks": [
            {"id": "b1", "type": "text", "title": "Introduction", "body": "Lesson content here..."},
            {"id": "b2", "type": "fill_blank", "title": "Practice", "instructions": "Fill in the blanks.",
             "items": [{"sentence": "__ is a greeting.", "answer": "Hello", "hint": "First word"}]},
        ]
    },
    "vocab": {
        "title": "New Vocabulary",
        "description": "Vocabulary description here",
        "words": [
            {"word": "hello", "translation": "नमस्ते", "example": "Hello, how are you?",
             "example_translation": "नमस्ते, आप कैसे हैं?"}
        ],
        "exercises": [
            {"type": "translation", "prompt": "Translate: Hello", "answer": "नमस्ते"}
        ]
    },
    "reading": {
        "title": "New Reading",
        "description": "Reading description here",
        "passage": "Passage text here...",
        "questions": [
            {"id": "rq1", "type": "mcq", "question": "Sample question?",
             "options": ["Option A", "Option B", "Option C", "Option D"], "correct": 0}
        ]
    },
    "writing": {
        "title": "New Writing",
        "description": "Writing description here",
        "tasks": [
            {"prompt": "Write a sentence about...", "hint": "Use the vocabulary from lesson 1.",
             "sample_answer": "Sample answer here..."}
        ]
    },
    "listening": {
        "title": "New Listening",
        "description": "Listening description here",
        "transcript": "Audio transcript here...",
        "audio_url": None,
        "questions": [
            {"id": "lq1", "type": "gap_fill", "sentence": "The ___ is red.", "answer": "apple"}
        ]
    },
    "speaking": {
        "title": "New Speaking",
        "description": "Speaking description here",
        "scenarios": [
            {"prompt": "Introduce yourself in the target language.", "expected_topics": ["name", "greeting"]}
        ]
    },
    "pronunciation": {
        "title": "New Pronunciation",
        "description": "Pronunciation description here",
        "items": [
            {"target_text": "नमस्ते", "romanization": "Namaste", "audio_url": None}
        ]
    },
    "test": {
        "title": "New Test",
        "description": "Test description here",
        "questions": [
            {"id": "tq1", "question": "Sample test question?",
             "options": ["A", "B", "C", "D"], "correct": 0}
        ]
    },
}


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


# ── Analytics [NEW] ────────────────────────────────────────────

@router.get("/analytics")
def get_analytics(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Per-activity-type analytics: completion count, avg score, pass rate.
    Also returns top 5 users by XP and recent completions.
    """
    # Per activity type stats
    activity_stats_raw = db.query(
        ActivityCompletion.activity_type,
        func.count(ActivityCompletion.id).label("total"),
        func.avg(ActivityCompletion.score_earned).label("avg_score"),
        func.sum(
            func.cast(ActivityCompletion.passed, Integer)
        ).label("passed_count"),
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

    # Top 5 users by total XP across all language pairs
    top_users_raw = db.query(
        User.username,
        User.display_name,
        func.sum(UserLanguageProgress.total_xp).label("total_xp"),
    ).join(UserLanguageProgress, User.id == UserLanguageProgress.user_id
    ).group_by(User.id, User.username, User.display_name
    ).order_by(func.sum(UserLanguageProgress.total_xp).desc()
    ).limit(5).all()

    top_users = [
        {
            "username": u.username,
            "display_name": u.display_name,
            "total_xp": int(u.total_xp or 0),
        }
        for u in top_users_raw
    ]

    # Recent 10 completions
    recent_raw = db.query(ActivityCompletion).order_by(
        ActivityCompletion.completed_at.desc()
    ).limit(10).all()

    recent_completions = [
        {
            "activity_type": c.activity_type,
            "lang_pair_id": c.lang_pair_id,
            "score_earned": c.score_earned,
            "max_score": c.max_score,
            "passed": c.passed,
            "completed_at": c.completed_at.isoformat() if c.completed_at else None,
        }
        for c in recent_raw
    ]

    # Language pair enrollment counts
    pair_enrollments_raw = db.query(
        UserLanguageProgress.lang_pair_id,
        func.count(UserLanguageProgress.id).label("cnt"),
        func.sum(UserLanguageProgress.total_xp).label("total_xp"),
    ).group_by(UserLanguageProgress.lang_pair_id).all()

    pair_enrollments = [
        {
            "lang_pair_id": r.lang_pair_id,
            "enrolled_users": int(r.cnt or 0),
            "total_xp": int(r.total_xp or 0),
        }
        for r in pair_enrollments_raw
    ]

    return {
        "activity_stats": activity_stats,
        "top_users": top_users,
        "recent_completions": recent_completions,
        "pair_enrollments": pair_enrollments,
    }


# ── Activity Types [NEW] ──────────────────────────────────────

@router.get("/activity-types")
def get_activity_types(admin: User = Depends(require_admin)):
    """Return metadata for all supported activity types + JSON templates."""
    return {
        "activity_types": [
            {**{"id": k}, **v}
            for k, v in ACTIVITY_TYPES.items()
        ],
        "templates": ACTIVITY_TEMPLATES,
    }


# ── Users ──────────────────────────────────────────────────────

@router.get("/users", response_model=List[AdminUserOut])
def list_users(
    search: Optional[str] = Query(None, description="Filter by username or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
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
    """[NEW] Re-activate a previously deactivated user account."""
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
    # Enrich with meta if available
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

    # Check for duplicate
    existing_pairs = content_service.get_all_pairs()
    if any(p["pairId"] == pair_id for p in existing_pairs):
        raise HTTPException(
            status_code=409,
            detail=f"Language pair '{pair_id}' already exists."
        )

    content_service.create_pair_directory(pair_id)
    content_service.register_pair(pair_id, req.source_lang_id, req.target_lang_id)

    meta = {
        "_comment": f"{req.source_lang_name} → {req.target_lang_name} language pair",
        "pairId": pair_id,
        "source": {"id": req.source_lang_id, "name": req.source_lang_name, "flag": req.source_lang_flag},
        "target": {"id": req.target_lang_id, "name": req.target_lang_name, "flag": req.target_lang_flag},
        "totalMonths": 6,
        "status": "active",
        "months": [],
    }
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
    Add a new activity JSON file to an existing language pair.
    Raises 409 if the file already exists to prevent accidental overwrites.
    """
    from app.services.content_service import _base_path
    try:
        file_path = _base_path(pair_id) / req.file_path
    except ValueError:
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
    file: str = Query(..., description="Relative file path to delete, e.g. month-1/week-1-lesson.json"),
    admin: User = Depends(require_admin),
):
    """[NEW] Delete a specific activity file from a language pair."""
    from app.services.content_service import _base_path
    try:
        base = _base_path(pair_id)
        file_path = base / file
        # Security: prevent path traversal
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
