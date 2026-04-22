"""
backend/tests/test_friends.py
Tests for friend system endpoints.
Uses inline register/login helpers instead of removed conftest helpers.
"""
import pytest
import uuid as _uuid


def register_user(client, username, email, password):
    """Register and return the response JSON."""
    return client.post("/api/auth/register", json={
        "username": username, "email": email,
        "password": password, "native_lang": "hi",
    })


def get_auth_headers(client, username, email, password):
    """Register (if needed) and return auth headers."""
    resp = register_user(client, username, email, password)
    if resp.status_code not in (200, 201):
        # Already registered — login instead
        resp = client.post("/api/auth/login", json={"email": email, "password": password})
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


class TestFriendsList:
    def test_friends_empty(self, client, auth_headers):
        res = client.get("/api/friends", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["friends"] == []

    def test_friends_unauthenticated(self, client):
        res = client.get("/api/friends")
        assert res.status_code in (401, 403)


class TestFriendRequests:
    def test_get_incoming_requests_empty(self, client, auth_headers):
        res = client.get("/api/friends/requests", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["requests"] == []

    def test_send_friend_request(self, client, auth_headers):
        uid = _uuid.uuid4().hex[:6]
        reg = register_user(client, f"ftarget{uid}", f"ftarget{uid}@ex.com", "SecurePass123")
        target_id = reg.json()["user"]["id"]

        res = client.post(f"/api/friends/request/{target_id}", headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "request_id" in data

    def test_cannot_send_request_to_self(self, client, auth_headers):
        my_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
        res = client.post(f"/api/friends/request/{my_id}", headers=auth_headers)
        assert res.status_code == 400

    def test_cannot_send_duplicate_request(self, client, auth_headers):
        uid = _uuid.uuid4().hex[:6]
        reg = register_user(client, f"dup{uid}", f"dup{uid}@ex.com", "SecurePass123")
        target_id = reg.json()["user"]["id"]
        client.post(f"/api/friends/request/{target_id}", headers=auth_headers)
        res = client.post(f"/api/friends/request/{target_id}", headers=auth_headers)
        assert res.status_code == 400

    def test_request_appears_in_incoming(self, client):
        uid = _uuid.uuid4().hex[:6]
        sender_hdrs = get_auth_headers(client, f"sndr{uid}", f"sndr{uid}@ex.com", "SecurePass123")
        recv_hdrs = get_auth_headers(client, f"recv{uid}", f"recv{uid}@ex.com", "SecurePass123")
        receiver_id = client.get("/api/auth/me", headers=recv_hdrs).json()["id"]
        client.post(f"/api/friends/request/{receiver_id}", headers=sender_hdrs)
        res = client.get("/api/friends/requests", headers=recv_hdrs)
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_send_request_to_nonexistent_user(self, client, auth_headers):
        res = client.post(f"/api/friends/request/{_uuid.uuid4()}", headers=auth_headers)
        assert res.status_code == 404


class TestAcceptDeclineRequest:
    def _setup(self, client):
        uid = _uuid.uuid4().hex[:6]
        s = get_auth_headers(client, f"sndr{uid}", f"sndr{uid}@ex.com", "SecurePass123")
        r = get_auth_headers(client, f"rcvr{uid}", f"rcvr{uid}@ex.com", "SecurePass123")
        rec_id = client.get("/api/auth/me", headers=r).json()["id"]
        req_id = client.post(f"/api/friends/request/{rec_id}", headers=s).json()["request_id"]
        return s, r, req_id

    def test_accept_request(self, client):
        sender, receiver, req_id = self._setup(client)
        res = client.put(f"/api/friends/request/{req_id}/accept", headers=receiver)
        assert res.status_code == 200
        friends = client.get("/api/friends", headers=receiver).json()
        assert friends["total"] >= 1

    def test_decline_request(self, client):
        sender, receiver, req_id = self._setup(client)
        res = client.put(f"/api/friends/request/{req_id}/decline", headers=receiver)
        assert res.status_code == 200

    def test_sender_cannot_accept_own_request(self, client):
        sender, receiver, req_id = self._setup(client)
        res = client.put(f"/api/friends/request/{req_id}/accept", headers=sender)
        assert res.status_code == 404


class TestRemoveFriend:
    def test_remove_friend(self, client):
        uid = _uuid.uuid4().hex[:6]
        u1 = get_auth_headers(client, f"rm1{uid}", f"rm1{uid}@ex.com", "SecurePass123")
        u2 = get_auth_headers(client, f"rm2{uid}", f"rm2{uid}@ex.com", "SecurePass123")
        u2_id = client.get("/api/auth/me", headers=u2).json()["id"]
        req_id = client.post(f"/api/friends/request/{u2_id}", headers=u1).json()["request_id"]
        client.put(f"/api/friends/request/{req_id}/accept", headers=u2)
        res = client.delete(f"/api/friends/{u2_id}", headers=u1)
        assert res.status_code == 200
        assert client.get("/api/friends", headers=u1).json()["total"] == 0

    def test_remove_nonexistent_friend(self, client, auth_headers):
        res = client.delete(f"/api/friends/{_uuid.uuid4()}", headers=auth_headers)
        assert res.status_code == 404
