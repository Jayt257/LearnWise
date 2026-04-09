"""
backend/app/routers/content.py
Content delivery endpoints — serves JSON data files from backend/data/.
  GET /api/content/pairs              - List all language pairs
  GET /api/content/{pair_id}/meta     - Get meta.json for a pair
  GET /api/content/{pair_id}/activity - Get a specific activity JSON file
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
    """Get meta.json for a language pair (roadmap structure)."""
    try:
        return content_service.get_meta(pair_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Language pair '{pair_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pair_id}/activity")
def get_activity(
    pair_id: str,
    file: str = Query(..., description="Relative file path, e.g. 'month-1/week-1-lesson.json'")
) -> Dict[str, Any]:
    """Get a specific activity's JSON content."""
    try:
        return content_service.get_activity(pair_id, file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Activity file '{file}' not found")
    except PermissionError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
