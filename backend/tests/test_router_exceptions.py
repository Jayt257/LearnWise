import pytest
from unittest.mock import patch
from app.main import app
from app.core.dependencies import get_db

def override_get_db_error():
    raise Exception("DB Error")

def test_admin_router_exceptions(client, admin_headers):
    # Test DB exception
    app.dependency_overrides[get_db] = override_get_db_error
    resp = client.get("/api/admin/users", headers=admin_headers)
    assert resp.status_code == 500
    app.dependency_overrides.clear()

    with patch("app.services.content_service.list_pair_files", side_effect=Exception("Error")):
        resp = client.get("/api/admin/content/hi-ja", headers=admin_headers)
        assert resp.status_code == 500
        
    with patch("app.services.content_service.get_activity", side_effect=Exception("Error")):
        resp = client.get("/api/admin/content/hi-ja/file?file=x.json", headers=admin_headers)
        assert resp.status_code == 500

    with patch("app.services.content_service.write_activity", side_effect=Exception("Error")):
        resp = client.put("/api/admin/content/hi-ja", headers=admin_headers, json={"file_path": "x", "content": {}})
        assert resp.status_code == 500
        resp = client.post("/api/admin/content/hi-ja/activity", headers=admin_headers, json={"file_path": "x", "content": {}})
        assert resp.status_code == 500

    with patch("app.services.content_service.write_meta", side_effect=Exception("Error")):
        resp = client.put("/api/admin/content/hi-ja/meta", headers=admin_headers, json={"file_path": "x", "content": {}})
        assert resp.status_code == 500

    with patch("os.remove", side_effect=Exception("Error")):
        with patch("pathlib.Path.exists", return_value=True):
            resp = client.delete("/api/admin/content/hi-ja/activity?file=x.json", headers=admin_headers)
            assert resp.status_code == 500

    with patch("app.services.content_service.add_month", side_effect=Exception("Error")):
        resp = client.post("/api/admin/content/hi-ja/month", headers=admin_headers)
        assert resp.status_code == 500

    with patch("app.services.content_service.add_block", side_effect=Exception("Error")):
        resp = client.post("/api/admin/content/hi-ja/month/1/block", headers=admin_headers)
        assert resp.status_code == 500

    with patch("shutil.rmtree", side_effect=Exception("Error")):
        with patch("app.services.content_service.get_meta", return_value={"months": [{"month": 1, "blocks": [{"block": 1}]}]}):
            with patch("app.services.content_service.write_meta"):
                with patch("pathlib.Path.exists", return_value=True):
                    resp = client.delete("/api/admin/content/hi-ja/month/1", headers=admin_headers)
                    assert resp.status_code == 500
                    resp = client.delete("/api/admin/content/hi-ja/month/1/block/1", headers=admin_headers)
                    assert resp.status_code == 500

def test_content_router_exceptions(client, auth_headers):
    with patch("app.services.content_service.get_all_pairs", side_effect=Exception("Error")):
        resp = client.get("/api/content/pairs", headers=auth_headers)
        assert resp.status_code == 500

    with patch("app.services.content_service.get_meta", side_effect=Exception("Error")):
        resp = client.get("/api/content/hi-ja/meta", headers=auth_headers)
        assert resp.status_code == 500

    with patch("app.services.content_service.get_activity", side_effect=Exception("Error")):
        resp = client.get("/api/content/hi-ja/activity?file=path.json", headers=auth_headers)
        assert resp.status_code == 500

def test_progress_router_exceptions(client, auth_headers):
    app.dependency_overrides[get_db] = override_get_db_error
    
    # Progress endpoints: /api/progress/...
    resp = client.get("/api/progress", headers=auth_headers)
    assert resp.status_code == 500
    
    resp = client.post("/api/progress/hi-ja/start", headers=auth_headers)
    assert resp.status_code == 500
    
    resp = client.get("/api/progress/hi-ja", headers=auth_headers)
    assert resp.status_code == 500
    
    resp = client.post("/api/progress/hi-ja/complete", headers=auth_headers, json={
        "month": 1, "block": 1, "activity_id": "M1B1_lesson_001", "activity_type": "lesson", "xp_earned": 10, "score_percentage": 100.0, "passed": True
    })
    assert resp.status_code == 500
    
    resp = client.get("/api/progress/hi-ja/completions?month=1&block=1", headers=auth_headers)
    assert resp.status_code == 500

    app.dependency_overrides.clear()
