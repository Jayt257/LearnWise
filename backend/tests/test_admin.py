"""
backend/tests/test_admin.py
Admin endpoint tests: stats, user management, language creation, content management.
"""
import pytest


def test_admin_stats_requires_admin(client, auth_headers):
    """Regular user must not access admin stats."""
    resp = client.get("/api/admin/stats", headers=auth_headers)
    assert resp.status_code == 403


def test_admin_stats(client, admin_headers):
    resp = client.get("/api/admin/stats", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "total_completions" in data
    assert "language_pairs" in data


def test_list_users(client, admin_headers):
    resp = client.get("/api/admin/users", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_users_with_search(client, admin_headers):
    resp = client.get("/api/admin/users?search=testlearner", headers=admin_headers)
    assert resp.status_code == 200


def test_get_activity_types(client, admin_headers):
    resp = client.get("/api/admin/activity-types", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "activity_types" in data
    assert "templates" in data
    types = [t["id"] for t in data["activity_types"]]
    for expected in ["lesson", "vocabulary", "pronunciation", "reading", "writing", "listening", "speaking", "test"]:
        assert expected in types


def test_get_activity_template(client, admin_headers):
    resp = client.get("/api/admin/activity-template/lesson", params={"pair_id": "hi-ja", "month": 1, "block": 1}, headers=admin_headers)
    assert resp.status_code == 200
    tmpl = resp.json()
    assert tmpl["activityType"] == "lesson"
    assert "lessonContent" in tmpl
    assert "adminCorrectAnswerSet" in tmpl


def test_get_activity_template_unknown_type(client, admin_headers):
    resp = client.get("/api/admin/activity-template/unknown_type", headers=admin_headers)
    assert resp.status_code == 400


def test_list_languages(client, admin_headers):
    resp = client.get("/api/admin/languages", headers=admin_headers)
    assert resp.status_code == 200
    langs = resp.json()
    assert isinstance(langs, list)
    pair_ids = [l["pairId"] for l in langs]
    assert "hi-ja" in pair_ids


def test_list_content(client, admin_headers):
    resp = client.get("/api/admin/content/hi-ja", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 145


def test_get_content_file(client, admin_headers):
    resp = client.get("/api/admin/content/hi-ja/file", params={"file": "month_1/block_1/M1B1_lesson.json"}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["activityType"] == "lesson"


def test_get_content_file_missing(client, admin_headers):
    resp = client.get("/api/admin/content/hi-ja/file", params={"file": "month_99/block_99/M99B99_lesson.json"}, headers=admin_headers)
    assert resp.status_code == 404


def test_get_analytics(client, admin_headers):
    resp = client.get("/api/admin/analytics", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "activity_stats" in data
    assert "top_users" in data
    assert "recent_completions" in data


def test_update_user_role(client, admin_headers, regular_user):
    resp = client.put(
        f"/api/admin/users/{regular_user.id}/role",
        headers=admin_headers,
        json={"role": "admin"}
    )
    assert resp.status_code == 200
    # Revert
    client.put(f"/api/admin/users/{regular_user.id}/role", headers=admin_headers, json={"role": "user"})


def test_deactivate_user(client, admin_headers, db):
    from app.models.user import User, UserRole
    from passlib.context import CryptContext
    _hash = lambda pw: CryptContext(schemes=["bcrypt"], deprecated="auto").hash(pw[:72])
    u = User(username="deactivateme", email="deactivate@test.com",
             password_hash=_hash("pass"), role=UserRole.user, is_active=True, native_lang="hi")
    db.add(u)
    db.commit()
    db.refresh(u)

    resp = client.delete(f"/api/admin/users/{u.id}", headers=admin_headers)
    assert resp.status_code == 200

    db.refresh(u)
    assert u.is_active is False


def test_create_new_language_pair(client, admin_headers):
    """Create a new language pair — directories and meta.json should be created."""
    pair_req = {
        "source_lang_id": "hi",
        "target_lang_id": "ko",
        "source_lang_name": "Hindi",
        "target_lang_name": "Korean",
        "source_lang_flag": "🇮🇳",
        "target_lang_flag": "🇰🇷",
    }
    resp = client.post("/api/admin/languages", headers=admin_headers, json=pair_req)
    assert resp.status_code in (200, 201), resp.text

    # Verify meta accessible
    meta_resp = client.get("/api/content/hi-ko/meta")
    assert meta_resp.status_code == 200
    meta = meta_resp.json()
    assert len(meta["months"]) == 3

    # Cleanup
    client.delete("/api/admin/languages/hi-ko", headers=admin_headers)


def test_create_duplicate_pair_rejected(client, admin_headers):
    resp = client.post("/api/admin/languages", headers=admin_headers, json={
        "source_lang_id": "hi", "target_lang_id": "ja",
        "source_lang_name": "Hindi", "target_lang_name": "Japanese",
        "source_lang_flag": "🇮🇳", "target_lang_flag": "🇯🇵",
    })
    assert resp.status_code == 409


def test_activate_user(client, admin_headers, db):
    from app.models.user import User, UserRole
    from passlib.context import CryptContext
    _hash = lambda pw: CryptContext(schemes=["bcrypt"], deprecated="auto").hash(pw[:72])
    u = User(username="activateme", email="activate@test.com",
             password_hash=_hash("pass"), role=UserRole.user, is_active=False, native_lang="hi")
    db.add(u)
    db.commit()
    db.refresh(u)

    # First activation
    resp = client.put(f"/api/admin/users/{u.id}/activate", headers=admin_headers)
    assert resp.status_code == 200

    # Second activation (already active)
    resp = client.put(f"/api/admin/users/{u.id}/activate", headers=admin_headers)
    assert resp.status_code == 200

    db.refresh(u)
    assert u.is_active is True


def test_update_content(client, admin_headers):
    # Try updating with dummy content
    resp = client.put("/api/admin/content/hi-ja", headers=admin_headers, json={
        "file_path": "month_1/block_1/dummy_update.json",
        "content": {"activityType": "lesson"}
    })
    assert resp.status_code == 200


def test_update_meta(client, admin_headers):
    # Just update the existing meta
    meta_resp = client.get("/api/content/hi-ja/meta")
    meta = meta_resp.json()
    resp = client.put("/api/admin/content/hi-ja/meta", headers=admin_headers, json={
        "file_path": "meta.json",
        "content": meta
    })
    assert resp.status_code == 200


def test_add_and_delete_activity(client, admin_headers):
    # Add new activity
    resp = client.post("/api/admin/content/hi-ja/activity", headers=admin_headers, json={
        "file_path": "month_1/block_1/M1B1_newact.json",
        "content": {"activityType": "test"}
    })
    assert resp.status_code == 201
    
    # Try adding again (conflict)
    resp = client.post("/api/admin/content/hi-ja/activity", headers=admin_headers, json={
        "file_path": "month_1/block_1/M1B1_newact.json",
        "content": {"activityType": "test"}
    })
    assert resp.status_code == 409

    # Delete it
    resp = client.delete("/api/admin/content/hi-ja/activity", params={"file": "month_1/block_1/M1B1_newact.json"}, headers=admin_headers)
    assert resp.status_code == 200

    # Delete missing
    resp = client.delete("/api/admin/content/hi-ja/activity", params={"file": "month_1/block_1/M1B1_newact.json"}, headers=admin_headers)
    assert resp.status_code == 404

    # Delete meta (should fail)
    resp = client.delete("/api/admin/content/hi-ja/activity", params={"file": "meta.json"}, headers=admin_headers)
    assert resp.status_code == 400


def test_admin_content_month_block_crud(client, admin_headers):
    # Create language pair to test on so we don't mess up hi-ja
    client.post("/api/admin/languages", headers=admin_headers, json={
         "source_lang_id": "hi", "target_lang_id": "zh",
         "source_lang_name": "Hindi", "target_lang_name": "Chinese",
         "source_lang_flag": "🇮🇳", "target_lang_flag": "🇨🇳",
    })
    
    # Add block
    resp = client.post("/api/admin/content/hi-zh/month/1/block", headers=admin_headers)
    assert resp.status_code == 201
    
    # Add month
    resp = client.post("/api/admin/content/hi-zh/month", headers=admin_headers)
    assert resp.status_code == 201

    # Delete block
    resp = client.delete("/api/admin/content/hi-zh/month/1/block/1", headers=admin_headers)
    assert resp.status_code == 200

    # Delete month
    resp = client.delete("/api/admin/content/hi-zh/month/1", headers=admin_headers)
    assert resp.status_code == 200
    
    # Cleanup
    client.delete("/api/admin/languages/hi-zh", headers=admin_headers)
