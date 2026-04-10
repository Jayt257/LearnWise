"""
backend/app/routers/content.py
Content delivery endpoints — serves JSON data from backend/data/languages/{src}/{tgt}/
  GET /api/content/pairs              - List all language pairs
  GET /api/content/{pair_id}/meta     - Get meta.json for a pair (full block structure)
  GET /api/content/{pair_id}/activity - Get a specific activity JSON file
  GET /api/content/{pair_id}/check    - Check if an activity file exists (for dynamic UI)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List
from app.services import content_service

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/pairs")
def list_pairs() -> List[Dict[str, Any]]:
    """List all registered language pairs."""
    try:
        return content_service.get_all_pairs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pair_id}/meta")
def get_meta(pair_id: str) -> Dict[str, Any]:
    """
    Get meta.json for a language pair (full block+activity roadmap structure).
    The meta is the single source of truth — frontend renders exactly what's here.
    """
    try:
        return content_service.get_meta(pair_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Language pair '{pair_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pair_id}/activity")
def get_activity(
    pair_id: str,
    file: str = Query(..., description="Relative file path, e.g. 'month_1/block_1/lesson.json'")
) -> Dict[str, Any]:
    """
    Get a specific activity's JSON content.
    Returns 404 if the file doesn't exist (admin hasn't created it yet).
    UI should handle 404 gracefully — show 'Content coming soon' state.
    """
    try:
        return content_service.get_activity(pair_id, file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Activity file '{file}' not found. Admin may not have created this content yet."
        )
    except PermissionError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pair_id}/check")
def check_activity_exists(
    pair_id: str,
    file: str = Query(..., description="Relative file path to check")
) -> Dict[str, Any]:
    """
    Check if an activity file exists without loading its content.
    Used by UI to show 'available' vs 'coming soon' state on activity cards.
    """
    try:
        from app.services.content_service import _base_path
        base = _base_path(pair_id)
        path = base / file
        path.resolve().relative_to(base.resolve())
        return {"exists": path.exists(), "file": file}
    except (ValueError, Exception):
        return {"exists": False, "file": file}
