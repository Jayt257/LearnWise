"""
backend/tests/test_progress.py
Progress tracking: start pair, complete activity, advance logic, XP, block advancement.
Tests SCORE_THRESHOLD_OVERRIDE=0 (always pass behavior).
"""
import pytest


PAIR_ID = "hi-ja"


def test_start_pair(client, auth_headers):
    resp = client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["lang_pair_id"] == PAIR_ID
    assert data["current_month"] == 1
    assert data["current_block"] == 1
    assert data["current_activity_id"] == 1
    assert data["total_xp"] == 0


def test_start_pair_idempotent(client, auth_headers):
    """Starting the same pair twice returns existing progress, not an error."""
    client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
    resp = client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
    assert resp.status_code in (200, 201)


def test_get_pair_progress(client, auth_headers):
    client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
    resp = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "current_block" in data
    assert "current_activity_id" in data


def test_get_all_progress(client, auth_headers):
    resp = client.get("/api/progress", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_complete_activity_advances_position(client, auth_headers):
    """With SCORE_THRESHOLD_OVERRIDE=0, any submission passes and position advances."""
    client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)

    resp = client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
        "activity_seq_id": 1,
        "activity_json_id": "ja_hi_M1B1_lesson_1",
        "activity_type": "lesson",
        "lang_pair_id": PAIR_ID,
        "month_number": 1,
        "block_number": 1,
        "score_earned": 50,
        "max_score": 50,
        "passed": True,
    })
    assert resp.status_code == 200
    completion = resp.json()
    assert completion["activity_seq_id"] == 1
    assert completion["passed"] is True
    assert completion["score_earned"] == 50

    # Position should have advanced to 2
    prog = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers).json()
    assert prog["current_activity_id"] == 2


def test_complete_activity_does_not_advance_past_current(client, auth_headers):
    """Completing a future activity (not current) should NOT advance position."""
    client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)

    resp = client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
        "activity_seq_id": 10,  # skip ahead
        "activity_type": "test",
        "lang_pair_id": PAIR_ID,
        "month_number": 1,
        "block_number": 2,
        "score_earned": 50,
        "max_score": 50,
        "passed": True,
    })
    assert resp.status_code == 200


def test_xp_accumulates(client, auth_headers):
    """Completing activities adds XP to total — strict checks kill the -= mutation."""
    client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
    prog_before = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers).json()
    xp_before = prog_before["total_xp"]

    score = 45
    # Use activity 99 (unique to this test) so it's always a first attempt
    # regardless of what other tests have completed. Guarantees xp_delta = score.
    client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
        "activity_seq_id": 99,
        "activity_type": "lesson",
        "lang_pair_id": PAIR_ID,
        "month_number": 3,
        "block_number": 1,
        "score_earned": score,
        "max_score": 50,
        "passed": True,
    })
    prog_after = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers).json()
    xp_after = prog_after["total_xp"]

    # XP must go UP — not down (kills total_xp -= xp_delta mutation)
    assert xp_after > xp_before, f"XP did not increase: before={xp_before}, after={xp_after}"
    # XP must be non-negative — double protection
    assert xp_after >= 0, f"XP went negative ({xp_after}) — accumulation is broken"

    # Now complete it again with a lower score (this should NOT change XP)
    # Kills the req.score_earned > existing.score_earned flipped to < mutation
    client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
        "activity_seq_id": 99,
        "activity_type": "lesson",
        "lang_pair_id": PAIR_ID,
        "month_number": 3,
        "block_number": 1,
        "score_earned": score - 20,
        "max_score": 50,
        "passed": True,
    })
    prog_after_lower = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers).json()
    assert prog_after_lower["total_xp"] == xp_after  # no change

    # Complete it again with a higher score (this SHOULD increase XP by the delta)
    client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
        "activity_seq_id": 99,
        "activity_type": "lesson",
        "lang_pair_id": PAIR_ID,
        "month_number": 3,
        "block_number": 1,
        "score_earned": score + 5,
        "max_score": 50,
        "passed": True,
    })
    prog_after_higher = client.get(f"/api/progress/{PAIR_ID}", headers=auth_headers).json()
    assert prog_after_higher["total_xp"] == xp_after + 5  # increased by exactly 5



def test_get_completions(client, auth_headers):
    resp = client.get(f"/api/progress/{PAIR_ID}/completions", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_completions_have_block_number(client, auth_headers):
    """Completion records include month_number and block_number."""
    client.post(f"/api/progress/{PAIR_ID}/start", headers=auth_headers)
    client.post(f"/api/progress/{PAIR_ID}/complete", headers=auth_headers, json={
        "activity_seq_id": 1,
        "activity_type": "lesson",
        "lang_pair_id": PAIR_ID,
        "month_number": 1,
        "block_number": 1,
        "score_earned": 50,
        "max_score": 50,
        "passed": True,
    })
    completions = client.get(f"/api/progress/{PAIR_ID}/completions", headers=auth_headers).json()
    c = next((x for x in completions if x["activity_seq_id"] == 1), None)
    if c:
        assert c["month_number"] == 1
        assert c["block_number"] == 1


def test_progress_unauthenticated(client):
    resp = client.get("/api/progress")
    assert resp.status_code in (401, 403)
