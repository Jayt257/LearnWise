import pytest
from unittest.mock import patch
from app.models.user import User, UserRole
from app.models.friends import FriendRequest, FriendRequestStatus
from app.models.progress import UserLanguageProgress, ActivityCompletion
from app.main import seed_admin

class TestModelRepr:
    """Covers __repr__ methods in all models."""

    def test_user_repr(self):
        u = User(username="test", role=UserRole.admin)
        assert repr(u) == "<User test (admin)>"

    def test_friends_repr(self):
        f = FriendRequest(sender_id="s_id", receiver_id="r_id", status=FriendRequestStatus.pending)
        assert repr(f) == "<FriendRequest s_id → r_id [pending]>"

    def test_progress_repr(self):
        p = UserLanguageProgress(user_id="u_id", lang_pair_id="hi-en", current_month=1, current_block=1, current_activity_id=1)
        assert repr(p) == "<Progress user=u_id pair=hi-en m=1 b=1 a=1>"

    def test_completion_repr(self):
        c = ActivityCompletion(activity_seq_id=1, activity_json_id="j_id", score_earned=10, max_score=100)
        assert repr(c) == "<Completion seqId=1 jsonId=j_id score=10/100>"


class TestMainCoverage:
    """Covers lines 46-48 in app/main.py"""

    def test_seed_admin_exception(self):
        # Trigger an exception inside seed_admin by mocking SessionLocal or query
        with patch("app.main.SessionLocal") as mock_session:
            mock_session.return_value.query.side_effect = Exception("DB error")
            # Should not blow up, just log and rollback
            seed_admin()


class TestAuthRouterCoverage:
    """Covers auth.py lines 42, 67, 81"""

    def test_register_username_taken(self, client, db):
        u = User(username="taken_user", email="avail@x.com", password_hash="123", role=UserRole.user)
        db.add(u)
        db.commit()
        resp = client.post("/api/auth/register", json={
            "username": "taken_user",
            "email": "another@x.com",
            "password": "Secure123!"
        })
        assert resp.status_code == 400
        assert "Username already taken" in resp.json()["detail"]
        db.delete(u)
        db.commit()

    def test_login_deactivated(self, client, db):
        u = User(username="deactivated_user", email="deact@x.com", password_hash="$2b$12$6MaHkuxGzeriYIqsVQQcQuNlPWA8XhxdDxXGpvDi84L0weqCwOZQu", role=UserRole.user, is_active=False)
        db.add(u)
        db.commit()
        resp = client.post("/api/auth/login", json={
            "email": "deact@x.com",
            "password": "testpassword123"
        })
        assert resp.status_code == 403
        assert "deactivated" in resp.json()["detail"]
        db.delete(u)
        db.commit()

    def test_admin_login_invalid(self, client, admin_user):
        resp = client.post("/api/auth/admin/login", json={
            "email": admin_user.email,
            "password": "wrongpassword"
        })
        assert resp.status_code == 401


class TestFriendsRouterCoverage:
    """Covers friends.py line 90"""

    def test_decline_request_not_found(self, client, auth_headers):
        import uuid
        resp = client.put(f"/api/friends/request/{uuid.uuid4()}/decline", headers=auth_headers)
        assert resp.status_code == 404


class TestLeaderboardRouterCoverage:
    """Covers leaderboard.py lines 77-80"""

    def test_friends_leaderboard_sender_receiver(self, client, regular_user, auth_headers, db):
        import uuid
        friend_id1 = uuid.uuid4()
        f1 = FriendRequest(sender_id=friend_id1, receiver_id=regular_user.id, status=FriendRequestStatus.accepted)
        
        friend_id2 = uuid.uuid4()
        f2 = FriendRequest(sender_id=regular_user.id, receiver_id=friend_id2, status=FriendRequestStatus.accepted)
        
        u1 = User(id=friend_id1, username="friend1", email="f1@f.com", password_hash="123", role=UserRole.user)
        u2 = User(id=friend_id2, username="friend2", email="f2@f.com", password_hash="123", role=UserRole.user)
        
        db.add_all([f1, f2, u1, u2])
        db.commit()

        resp = client.get("/api/leaderboard/hi-ja/friends", headers=auth_headers)
        assert resp.status_code == 200

        db.delete(f1)
        db.delete(f2)
        db.delete(u1)
        db.delete(u2)
        db.commit()


class TestContentRouterCoverage:
    """Covers content.py lines 35, 78-79"""

    def test_get_meta_file_not_found(self, client, auth_headers):
        with patch("app.services.content_service.get_meta", side_effect=FileNotFoundError):
            resp = client.get("/api/content/non-exist/meta")
            assert resp.status_code == 404

    def test_check_activity_exception(self, client, auth_headers):
        with patch("app.services.content_service._base_path", side_effect=Exception):
            resp = client.get("/api/content/hi-ja/check?file=fail.json")
            assert resp.status_code == 200
            assert resp.json() == {"exists": False, "file": "fail.json"}


class TestAdminRouterCoverage:
    """Covers admin.py edge case lines."""

    def test_list_users_role(self, client, admin_headers):
        resp = client.get("/api/admin/users?role=user", headers=admin_headers)
        assert resp.status_code == 200

    def test_update_role_invalid(self, client, admin_headers, regular_user):
        resp = client.put(f"/api/admin/users/{regular_user.id}/role", headers=admin_headers, json={"role": "superman"})
        assert resp.status_code == 400
        assert "Invalid role" in resp.json()["detail"]

    def test_update_role_not_found(self, client, admin_headers):
        import uuid
        resp = client.put(f"/api/admin/users/{uuid.uuid4()}/role", headers=admin_headers, json={"role": "admin"})
        assert resp.status_code == 404

    def test_deactivate_user_not_found(self, client, admin_headers):
        import uuid
        resp = client.delete(f"/api/admin/users/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404

    def test_deactivate_own_admin(self, client, admin_headers, admin_user):
        resp = client.delete(f"/api/admin/users/{admin_user.id}", headers=admin_headers)
        assert resp.status_code == 400

    def test_activate_user_not_found(self, client, admin_headers):
        import uuid
        resp = client.put(f"/api/admin/users/{uuid.uuid4()}/activate", headers=admin_headers)
        assert resp.status_code == 404

    def test_list_languages_meta_exception(self, client, admin_headers):
        with patch("app.services.content_service.get_all_pairs", return_value=[{"pairId": "hi-ja"}]):
            with patch("app.services.content_service.get_meta", side_effect=Exception):
                resp = client.get("/api/admin/languages", headers=admin_headers)
                assert resp.status_code == 200
                assert resp.json()[0]["meta"] is None

    def test_get_content_file_permission(self, client, admin_headers):
        with patch("app.services.content_service.get_activity", side_effect=PermissionError):
            resp = client.get("/api/admin/content/hi-ja/file?file=../secret", headers=admin_headers)
            assert resp.status_code == 403

    def test_update_content_permission(self, client, admin_headers):
        with patch("app.services.content_service.write_activity", side_effect=PermissionError):
            resp = client.put("/api/admin/content/hi-ja", headers=admin_headers, json={"file_path": "../a", "content": {}})
            assert resp.status_code == 403

    def test_add_activity_permission(self, client, admin_headers):
        with patch("pathlib.Path.resolve", side_effect=ValueError):
            resp = client.post("/api/admin/content/hi-ja/activity", headers=admin_headers, json={"file_path": "../a", "content": {}})
            assert resp.status_code == 403

    def test_delete_activity_permission(self, client, admin_headers):
        with patch("pathlib.Path.resolve", side_effect=ValueError):
            resp = client.delete("/api/admin/content/hi-ja/activity?file=../a", headers=admin_headers)
            assert resp.status_code == 403

    def test_delete_language_not_found(self, client, admin_headers):
        resp = client.delete("/api/admin/languages/non-existent-pair", headers=admin_headers)
        assert resp.status_code == 404

    def test_update_content_exception(self, client, admin_headers):
        with patch("app.services.content_service.write_activity", side_effect=Exception("Disk full")):
            resp = client.put("/api/admin/content/hi-ja", headers=admin_headers, json={"file_path": "a.json", "content": {}})
            assert resp.status_code == 500

    def test_update_meta_exception(self, client, admin_headers):
        with patch("app.services.content_service.write_meta", side_effect=Exception("Disk full")):
            resp = client.put("/api/admin/content/hi-ja/meta", headers=admin_headers, json={"file_path": "a", "content": {}})
            assert resp.status_code == 500

    def test_add_activity_invalid_pair(self, client, admin_headers):
        with patch("app.services.content_service._base_path", side_effect=Exception("Invalid pair")):
            resp = client.post("/api/admin/content/hi-ja/activity", headers=admin_headers, json={"file_path": "a.json", "content": {}})
            assert resp.status_code == 400

    def test_add_activity_exception(self, client, admin_headers):
        from unittest.mock import MagicMock
        with patch("app.services.content_service._base_path") as mock_path:
            mock_path.return_value.resolve.return_value.relative_to.return_value = "safe"
            # file doesn't exist
            mock_path.return_value.__truediv__.return_value.exists.return_value = False
            with patch("app.services.content_service.write_activity", side_effect=Exception("Fail")):
                resp = client.post("/api/admin/content/foo/activity", headers=admin_headers, json={"file_path": "a", "content": {}})
                assert resp.status_code == 500
    
    def test_delete_activity_invalid_pair(self, client, admin_headers):
        with patch("app.services.content_service._base_path", side_effect=Exception("Invalid")):
            resp = client.delete("/api/admin/content/foo/activity?file=a.json", headers=admin_headers)
            assert resp.status_code == 400

    def test_add_month_not_found(self, client, admin_headers):
        with patch("app.services.content_service.add_month", side_effect=FileNotFoundError):
            resp = client.post("/api/admin/content/foo/month", headers=admin_headers)
            assert resp.status_code == 404
            
    def test_add_month_exception(self, client, admin_headers):
        with patch("app.services.content_service.add_month", side_effect=Exception("Failure")):
            resp = client.post("/api/admin/content/foo/month", headers=admin_headers)
            assert resp.status_code == 500

    def test_add_block_not_found(self, client, admin_headers):
        with patch("app.services.content_service.add_block", side_effect=FileNotFoundError):
            resp = client.post("/api/admin/content/foo/month/1/block", headers=admin_headers)
            assert resp.status_code == 404

    def test_add_block_value_error(self, client, admin_headers):
        with patch("app.services.content_service.add_block", side_effect=ValueError("Invalid month")):
            resp = client.post("/api/admin/content/foo/month/1/block", headers=admin_headers)
            assert resp.status_code == 404

    def test_add_block_exception(self, client, admin_headers):
        with patch("app.services.content_service.add_block", side_effect=Exception("Failure")):
            resp = client.post("/api/admin/content/foo/month/1/block", headers=admin_headers)
            assert resp.status_code == 500

    def test_delete_block_not_found(self, client, admin_headers):
        with patch("app.services.content_service.get_meta", return_value={"months": []}):
            resp = client.delete("/api/admin/content/hi-ja/month/1/block/1", headers=admin_headers)
            assert resp.status_code == 404
            
    def test_delete_block_inner_not_found(self, client, admin_headers):
        with patch("app.services.content_service.get_meta", return_value={"months": [{"month": 1, "blocks": []}]}):
            resp = client.delete("/api/admin/content/hi-ja/month/1/block/1", headers=admin_headers)
            assert resp.status_code == 404

    def test_delete_block_exception(self, client, admin_headers):
        with patch("app.services.content_service.get_meta", side_effect=Exception("Fail")):
            resp = client.delete("/api/admin/content/hi-ja/month/1/block/1", headers=admin_headers)
            assert resp.status_code == 500

    def test_delete_month_not_found(self, client, admin_headers):
        with patch("app.services.content_service.get_meta", return_value={"months": []}):
            resp = client.delete("/api/admin/content/hi-ja/month/1", headers=admin_headers)
            assert resp.status_code == 404

    def test_delete_month_exception(self, client, admin_headers):
        with patch("app.services.content_service.get_meta", side_effect=Exception("Fail")):
            resp = client.delete("/api/admin/content/hi-ja/month/1", headers=admin_headers)
            assert resp.status_code == 500

    def test_analytics_with_completions(self, client, admin_headers, regular_user, db):
        """Covers admin.py lines 371-373: the activity_stats row parsing loop."""
        completion = ActivityCompletion(
            user_id=regular_user.id,
            lang_pair_id="hi-en",
            activity_seq_id=99,
            activity_json_id="lesson_analytics_test",
            activity_type="lesson",
            score_earned=80,
            max_score=100,
            passed=True,
        )
        db.add(completion)
        db.commit()

        resp = client.get("/api/admin/analytics", headers=admin_headers)
        assert resp.status_code == 200
        assert "activity_stats" in resp.json()

        db.delete(completion)
        db.commit()
