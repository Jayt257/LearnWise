"""
backend/tests/test_content.py
Content API tests: list pairs, get meta, get activity by file path,
check missing activity returns 404 (not crash), check endpoint.
"""
import pytest

PAIR_ID = "hi-ja"
LESSON_FILE = "month_1/block_1/lesson.json"
VOCAB_FILE = "month_1/block_1/vocabulary.json"
TEST_FILE = "month_1/block_1/test.json"
MISSING_FILE = "month_1/block_99/lesson.json"


def test_list_pairs(client):
    resp = client.get("/api/content/pairs")
    assert resp.status_code == 200
    pairs = resp.json()
    assert isinstance(pairs, list)
    pair_ids = [p["pairId"] for p in pairs]
    assert PAIR_ID in pair_ids


def test_get_meta(client):
    resp = client.get(f"/api/content/{PAIR_ID}/meta")
    assert resp.status_code == 200
    meta = resp.json()
    assert "months" in meta
    assert len(meta["months"]) == 3

    # Check structure: each month has blocks, each block has 8 activities
    for month in meta["months"]:
        assert "blocks" in month
        assert "title" in month
        assert "targetLevel" in month
        for block in month["blocks"]:
            assert "activities" in block
            assert len(block["activities"]) == 8
            for act in block["activities"]:
                assert "id" in act
                assert "type" in act
                assert "file" in act
                assert "xp" in act


def test_get_lesson_activity(client):
    resp = client.get(f"/api/content/{PAIR_ID}/activity", params={"file": LESSON_FILE})
    assert resp.status_code == 200
    data = resp.json()
    assert data["activityType"] == "lesson"
    assert "lessonContent" in data
    assert isinstance(data["lessonContent"], list)


def test_get_vocabulary_activity(client):
    resp = client.get(f"/api/content/{PAIR_ID}/activity", params={"file": VOCAB_FILE})
    assert resp.status_code == 200
    data = resp.json()
    assert data["activityType"] == "vocabulary"
    assert "wordList" in data
    assert len(data["wordList"]) > 0


def test_get_test_activity(client):
    resp = client.get(f"/api/content/{PAIR_ID}/activity", params={"file": TEST_FILE})
    assert resp.status_code == 200
    data = resp.json()
    assert data["activityType"] == "test"
    # Test has sections[]
    sections = data.get("sections") or data.get("questionSections") or []
    assert len(sections) > 0


def test_missing_activity_returns_404(client):
    """A missing activity file should return 404, not 500."""
    resp = client.get(f"/api/content/{PAIR_ID}/activity", params={"file": MISSING_FILE})
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert "not found" in detail.lower()


def test_check_existing_activity(client):
    resp = client.get(f"/api/content/{PAIR_ID}/check", params={"file": LESSON_FILE})
    assert resp.status_code == 200
    assert resp.json()["exists"] is True


def test_check_missing_activity(client):
    resp = client.get(f"/api/content/{PAIR_ID}/check", params={"file": MISSING_FILE})
    assert resp.status_code == 200
    assert resp.json()["exists"] is False


def test_path_traversal_blocked(client):
    """Ensure path traversal attempts are rejected."""
    resp = client.get(f"/api/content/{PAIR_ID}/activity", params={"file": "../../backend/.env"})
    assert resp.status_code in (400, 403, 404)


def test_meta_has_source_and_target(client):
    resp = client.get(f"/api/content/{PAIR_ID}/meta")
    meta = resp.json()
    assert "source" in meta
    assert "target" in meta
    assert meta["source"]["id"] == "hi"
    assert meta["target"]["id"] == "ja"


def test_meta_activity_ids_are_sequential(client):
    """All 144 activity IDs in meta must be unique sequential integers."""
    meta = client.get(f"/api/content/{PAIR_ID}/meta").json()
    all_ids = []
    for month in meta["months"]:
        for block in month["blocks"]:
            for act in block["activities"]:
                all_ids.append(act["id"])

    assert len(all_ids) == 144
    assert sorted(all_ids) == list(range(1, 145))
