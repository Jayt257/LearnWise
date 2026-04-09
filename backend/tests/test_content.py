"""
backend/tests/test_content.py
Tests for content delivery endpoints:
  GET /api/content/pairs
  GET /api/content/{pair_id}/meta
  GET /api/content/{pair_id}/activity
"""

import json
import os
import pytest
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────

def _create_sample_pair(tmp_data_dir: Path, pair_id: str = "test-en"):
    """Create a minimal test language pair directory structure."""
    src, tgt = pair_id.split("-")
    pair_dir = tmp_data_dir / "languages" / src / tgt
    pair_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "pairId": pair_id,
        "source": {"id": src, "name": "Test", "flag": "🧪"},
        "target": {"id": tgt, "name": "English", "flag": "🇬🇧"},
        "totalMonths": 1,
        "status": "active",
        "months": []
    }
    with open(pair_dir / "meta.json", "w") as f:
        json.dump(meta, f)

    month_dir = pair_dir / "month-1"
    month_dir.mkdir(exist_ok=True)
    activity = {"activityId": 1, "type": "lesson", "title": "Test Lesson", "blocks": []}
    with open(month_dir / "week-1-lesson.json", "w") as f:
        json.dump(activity, f)

    # Register in language_pairs.json
    pairs_file = tmp_data_dir / "language_pairs.json"
    pairs = []
    if pairs_file.exists():
        with open(pairs_file) as f:
            pairs = json.load(f)
    if pair_id not in [p["pairId"] for p in pairs]:
        pairs.append({"pairId": pair_id, "from": src, "to": tgt, "dataPath": f"{src}/{tgt}"})
    with open(pairs_file, "w") as f:
        json.dump(pairs, f)

    return pair_dir


@pytest.fixture(autouse=True)
def patch_data_path(tmp_path, monkeypatch):
    """Redirect content_service to use a temporary data directory."""
    from app.core import config
    monkeypatch.setattr(config.settings, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(
        "app.services.content_service.settings",
        config.settings,
    )
    # Patch the data_path property
    monkeypatch.setattr(
        config.settings.__class__,
        "data_path",
        property(lambda self: str(tmp_path)),
    )
    _create_sample_pair(tmp_path, "test-en")
    yield tmp_path


# ── Tests ─────────────────────────────────────────────────────

class TestPairsList:
    def test_list_pairs_returns_list(self, client):
        """GET /api/content/pairs returns a list."""
        res = client.get("/api/content/pairs")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_list_pairs_contains_registered_pair(self, client):
        """Registered pair appears in list."""
        res = client.get("/api/content/pairs")
        pair_ids = [p["pairId"] for p in res.json()]
        assert "test-en" in pair_ids


class TestGetMeta:
    def test_get_meta_success(self, client):
        """GET /api/content/test-en/meta returns meta.json."""
        res = client.get("/api/content/test-en/meta")
        assert res.status_code == 200
        data = res.json()
        assert data["pairId"] == "test-en"
        assert "source" in data
        assert "target" in data

    def test_get_meta_not_found(self, client):
        """Non-existent pair returns 404."""
        res = client.get("/api/content/xx-yy/meta")
        assert res.status_code == 404

    def test_get_meta_has_required_fields(self, client):
        """Meta includes all required fields."""
        res = client.get("/api/content/test-en/meta")
        data = res.json()
        for field in ["pairId", "source", "target", "totalMonths", "months"]:
            assert field in data, f"Missing field: {field}"


class TestGetActivity:
    def test_get_activity_success(self, client):
        """GET /api/content/test-en/activity?file=month-1/week-1-lesson.json returns content."""
        res = client.get(
            "/api/content/test-en/activity",
            params={"file": "month-1/week-1-lesson.json"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["activityId"] == 1
        assert data["type"] == "lesson"

    def test_get_activity_missing_file_param(self, client):
        """Missing file query param returns 422."""
        res = client.get("/api/content/test-en/activity")
        assert res.status_code == 422

    def test_get_activity_file_not_found(self, client):
        """Non-existent file returns 404."""
        res = client.get(
            "/api/content/test-en/activity",
            params={"file": "month-1/nonexistent.json"}
        )
        assert res.status_code == 404

    def test_get_activity_path_traversal_blocked(self, client):
        """Path traversal attempt returns 400."""
        res = client.get(
            "/api/content/test-en/activity",
            params={"file": "../../secrets.txt"}
        )
        assert res.status_code in (400, 404)
