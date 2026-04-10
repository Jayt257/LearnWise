"""
backend/app/services/content_service.py
Reads and writes JSON data files for language learning content.
Block-based structure: backend/data/languages/{src}/{tgt}/month_{N}/block_{M}/{type}.json

Key behaviors:
- list_pair_files: scans directory — if a file doesn't exist it simply won't appear
- get_meta: returns the meta.json which is the source of truth for roadmap
- Admin modifies meta.json and filesystem → frontend reflects changes automatically (no hardcoding)
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.config import settings

# Activity types per data_README (8 per block)
ACTIVITY_TYPES = ["lesson", "pronunciation", "reading", "writing", "listening", "vocabulary", "speaking", "test"]

# Month themes per data_README section 4
MONTH_THEMES = {
    1: {
        "title": "Understand the Language",
        "description": "Get comfortable with sound, script, and survival words",
        "targetLevel": "A1",
        "blocks": {
            1: "Orientation",
            2: "Sounds and Script",
            3: "Core Survival Words",
            4: "First Communication",
            5: "Culture Basics",
            6: "Review and Confidence Check",
        }
    },
    2: {
        "title": "Use the Language",
        "description": "Form sentences and communicate in simple daily situations",
        "targetLevel": "A1+",
        "blocks": {
            1: "Sentence Building",
            2: "Daily Vocabulary",
            3: "Listening Practice",
            4: "Reading Practice",
            5: "Speaking Practice",
            6: "Culture in Context",
        }
    },
    3: {
        "title": "Apply the Language",
        "description": "Have short real-world conversations with confidence",
        "targetLevel": "A2",
        "blocks": {
            1: "Travel and Survival Language",
            2: "Polite Communication",
            3: "Real-Life Scenarios",
            4: "Mixed Skill Practice",
            5: "Review and Correction",
            6: "Final Test",
        }
    },
}


def _base_path(pair_id: str) -> Path:
    """Returns the absolute path to backend/data/languages/{src}/{tgt}/"""
    parts = pair_id.split("-")  # "hi-ja" -> ["hi", "ja"]
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
    file_path is relative to pair root, e.g. 'month_1/block_1/lesson.json'
    Returns None if file doesn't exist (admin may not have created it yet).
    """
    base = _base_path(pair_id)
    path = base / file_path
    # Security: ensure path doesn't escape base
    try:
        path.resolve().relative_to(base.resolve())
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
    """List all JSON files in a language pair directory (excluding meta.json)."""
    base = _base_path(pair_id)
    if not base.exists():
        return []
    files = []
    for p in sorted(base.rglob("*.json")):
        if p.name == "meta.json":
            continue
        rel = str(p.relative_to(base))
        files.append({
            "path": rel,
            "size_bytes": p.stat().st_size,
            "month": _extract_part(rel, "month"),
            "block": _extract_part(rel, "block"),
            "activity_type": p.stem,
        })
    return files


def _extract_part(rel_path: str, part: str) -> Optional[int]:
    """Extract month or block number from path like 'month_1/block_2/lesson.json'"""
    try:
        parts = rel_path.replace("\\", "/").split("/")
        for p in parts:
            if p.startswith(part + "_"):
                return int(p.split("_")[1])
    except Exception:
        pass
    return None


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


def _build_meta_skeleton(pair_id: str, src_id: str, tgt_id: str,
                          src_name: str, tgt_name: str,
                          src_flag: str, tgt_flag: str,
                          total_months: int = 3, blocks_per_month: int = 6) -> Dict[str, Any]:
    """Build a fresh meta.json skeleton following data_README block structure."""
    months = []
    global_id = 1
    xp_per_activity = 50

    for m in range(1, total_months + 1):
        theme = MONTH_THEMES.get(m, {
            "title": f"Month {m}",
            "description": f"Month {m} learning content",
            "targetLevel": "A1",
            "blocks": {}
        })
        blocks = []
        for b in range(1, blocks_per_month + 1):
            block_title = theme["blocks"].get(b, f"Block {b}")
            block_code = f"M{m}B{b}"
            activities = []
            for activity_type in ACTIVITY_TYPES:
                xp = 100 if activity_type == "test" else xp_per_activity
                activities.append({
                    "id": global_id,
                    "type": activity_type,
                    "file": f"month_{m}/block_{b}/M{m}B{b}_{activity_type}.json",
                    "xp": xp
                })
                global_id += 1
            blocks.append({
                "block": b,
                "blockCode": block_code,
                "title": block_title,
                "activities": activities
            })
        months.append({
            "month": m,
            "title": theme["title"],
            "description": theme["description"],
            "targetLevel": theme["targetLevel"],
            "blocks": blocks
        })

    return {
        "_comment": f"{src_name} → {tgt_name} language pair",
        "_version": "4.0",
        "pairId": pair_id,
        "source": {"id": src_id, "name": src_name, "flag": src_flag},
        "target": {"id": tgt_id, "name": tgt_name, "flag": tgt_flag},
        "totalMonths": total_months,
        "status": "active",
        "months": months,
    }


def create_pair_directory(pair_id: str, src_id: str = None, tgt_id: str = None,
                          src_name: str = None, tgt_name: str = None,
                          src_flag: str = "🏳", tgt_flag: str = "🏳",
                          total_months: int = 3) -> Path:
    """
    Create directory structure for a new language pair.
    Scaffolds: month_1/block_1/ through month_{N}/block_6/ directories.
    Does NOT create activity JSON files — admin creates them later.
    """
    base = _base_path(pair_id)
    base.mkdir(parents=True, exist_ok=True)

    for m in range(1, total_months + 1):
        for b in range(1, 7):  # 6 blocks per month
            block_dir = base / f"month_{m}" / f"block_{b}"
            block_dir.mkdir(parents=True, exist_ok=True)

    return base


def add_month(pair_id: str) -> Dict[str, Any]:
    """
    Add a new month to an existing language pair.
    Creates directory structure and updates meta.json.
    Returns updated meta.
    """
    meta = get_meta(pair_id)
    existing_months = [m["month"] for m in meta.get("months", [])]
    new_month_num = max(existing_months, default=0) + 1

    # Create directories
    base = _base_path(pair_id)
    theme = MONTH_THEMES.get(new_month_num, {
        "title": f"Month {new_month_num}",
        "description": f"Month {new_month_num} content",
        "targetLevel": "A2+",
        "blocks": {}
    })

    # Find next global activity ID
    all_ids = []
    for m in meta.get("months", []):
        for bl in m.get("blocks", []):
            for act in bl.get("activities", []):
                all_ids.append(act["id"])
    next_id = max(all_ids, default=0) + 1

    blocks = []
    for b in range(1, 7):
        block_dir = base / f"month_{new_month_num}" / f"block_{b}"
        block_dir.mkdir(parents=True, exist_ok=True)
        block_title = theme["blocks"].get(b, f"Block {b}")
        block_code = f"M{new_month_num}B{b}"
        activities = []
        for activity_type in ACTIVITY_TYPES:
            xp = 100 if activity_type == "test" else 50
            activities.append({
                "id": next_id,
                "type": activity_type,
                "file": f"month_{new_month_num}/block_{b}/M{new_month_num}B{b}_{activity_type}.json",
                "xp": xp
            })
            next_id += 1
        blocks.append({
            "block": b,
            "blockCode": block_code,
            "title": block_title,
            "activities": activities
        })

    meta["months"].append({
        "month": new_month_num,
        "title": theme["title"],
        "description": theme["description"],
        "targetLevel": theme["targetLevel"],
        "blocks": blocks
    })
    meta["totalMonths"] = new_month_num
    write_meta(pair_id, meta)
    return meta


def add_block(pair_id: str, month_number: int) -> Dict[str, Any]:
    """
    Add a new block to an existing month in a language pair.
    Creates directory and updates meta.json.
    Returns updated meta.
    """
    meta = get_meta(pair_id)
    month_data = next((m for m in meta.get("months", []) if m["month"] == month_number), None)
    if not month_data:
        raise ValueError(f"Month {month_number} not found in pair {pair_id}")

    existing_blocks = [bl["block"] for bl in month_data.get("blocks", [])]
    new_block_num = max(existing_blocks, default=0) + 1

    # Find next global activity ID
    all_ids = []
    for m in meta.get("months", []):
        for bl in m.get("blocks", []):
            for act in bl.get("activities", []):
                all_ids.append(act["id"])
    next_id = max(all_ids, default=0) + 1

    # Create directory
    base = _base_path(pair_id)
    block_dir = base / f"month_{month_number}" / f"block_{new_block_num}"
    block_dir.mkdir(parents=True, exist_ok=True)

    block_code = f"M{month_number}B{new_block_num}"
    activities = []
    for activity_type in ACTIVITY_TYPES:
        xp = 100 if activity_type == "test" else 50
        activities.append({
            "id": next_id,
            "type": activity_type,
            "file": f"month_{month_number}/block_{new_block_num}/M{month_number}B{new_block_num}_{activity_type}.json",
            "xp": xp
        })
        next_id += 1

    month_data["blocks"].append({
        "block": new_block_num,
        "blockCode": block_code,
        "title": f"Block {new_block_num}",
        "activities": activities
    })
    write_meta(pair_id, meta)
    return meta


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
    """Remove a language pair directory + registry entry. Clean up parent if empty."""
    base = _base_path(pair_id)
    if base.exists():
        import shutil
        shutil.rmtree(base)
        # Check if parent is empty
        parent = base.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    pairs = get_all_pairs()
    pairs = [p for p in pairs if p["pairId"] != pair_id]
    path = Path(settings.data_path) / "language_pairs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)
