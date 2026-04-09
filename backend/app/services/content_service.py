"""
backend/app/services/content_service.py
Reads and writes JSON data files for language learning content.
All paths are relative to backend/data/languages/{source}/{target}/
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.config import settings


def _base_path(pair_id: str) -> Path:
    """Returns the absolute path to backend/data/languages/{src}/{tgt}/"""
    parts = pair_id.split("-")  # "hi-en" -> ["hi", "en"]
    if len(parts) != 2:
        raise ValueError(f"Invalid pair_id: {pair_id}")
    src, tgt = parts
    p = Path(settings.data_path) / "languages" / src / tgt
    return p


def get_meta(pair_id: str) -> Dict[str, Any]:
    """Load meta.json for a language pair."""
    path = _base_path(pair_id) / "meta.json"
    if not path.exists():
        raise FileNotFoundError(f"meta.json not found for pair: {pair_id}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_activity(pair_id: str, file_path: str) -> Dict[str, Any]:
    """
    Load a specific activity JSON file.
    file_path is relative to pair root, e.g. 'month-1/week-1-lesson.json'
    """
    path = _base_path(pair_id) / file_path
    # Security: ensure path doesn't escape base
    try:
        path.resolve().relative_to(_base_path(pair_id).resolve())
    except ValueError:
        raise PermissionError("Path traversal attempt detected")
    if not path.exists():
        raise FileNotFoundError(f"Activity file not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_pairs() -> List[Dict[str, Any]]:
    """Read language_pairs.json registry."""
    path = Path(settings.data_path) / "language_pairs.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_pair_files(pair_id: str) -> List[Dict[str, Any]]:
    """List all JSON files in a language pair directory."""
    base = _base_path(pair_id)
    if not base.exists():
        return []
    files = []
    for p in sorted(base.rglob("*.json")):
        rel = str(p.relative_to(base))
        files.append({"path": rel, "size_bytes": p.stat().st_size})
    return files


def write_activity(pair_id: str, file_path: str, content: Dict[str, Any]) -> None:
    """Write (overwrite) an activity JSON file. Used by admin."""
    path = _base_path(pair_id) / file_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


def write_meta(pair_id: str, content: Dict[str, Any]) -> None:
    """Write meta.json for a language pair."""
    path = _base_path(pair_id) / "meta.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


def create_pair_directory(pair_id: str) -> Path:
    """Create directory structure for a new language pair."""
    base = _base_path(pair_id)
    base.mkdir(parents=True, exist_ok=True)
    (base / "month-1").mkdir(exist_ok=True)
    return base


def register_pair(pair_id: str, src_id: str, tgt_id: str) -> None:
    """Add a new pair to language_pairs.json."""
    pairs = get_all_pairs()
    existing_ids = [p["pairId"] for p in pairs]
    if pair_id not in existing_ids:
        pairs.append({
            "pairId": pair_id,
            "from": src_id,
            "to": tgt_id,
            "dataPath": f"{src_id}/{tgt_id}"
        })
        path = Path(settings.data_path) / "language_pairs.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(pairs, f, ensure_ascii=False, indent=2)


def delete_pair(pair_id: str) -> None:
    """Remove a language pair directory + registry entry."""
    base = _base_path(pair_id)
    if base.exists():
        shutil.rmtree(base)
    pairs = get_all_pairs()
    pairs = [p for p in pairs if p["pairId"] != pair_id]
    path = Path(settings.data_path) / "language_pairs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)
