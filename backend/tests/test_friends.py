"""
backend/tests/test_friends.py
Tests for friend system endpoints:
  GET    /api/friends
  GET    /api/friends/requests
  POST   /api/friends/request/{user_id}
  PUT    /api/friends/request/{req_id}/accept
  PUT    /api/friends/request/{req_id}/decline
  DELETE /api/friends/{user_id}
"""

import pytest
from tests.conftest import get_auth_headers, register_user


class TestFriendsList:
    def test_friends_empty(self, client, auth_headers):
        """New user has no friends."""
        res = client.get("/api/friends", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["friends"] == []

    def test_friends_unauthenticated(self, client):
        res = client.get("/api/friends")
        assert res.status_code == 401


class TestFriendRequests:
    def test_get_incoming_requests_empty(self, client, auth_headers):
        """New user has no pending requests."""
        res = client.get("/api/friends/requests", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["requests"] == []

    def test_send_friend_request(self, client, auth_headers):
        """Sending a request to another user returns 201."""
        # Register a second user
        reg = register_user(client, "friend_target", "target@example.com", "SecurePass123")
        target_id = reg.json()["user"]["id"]

        res = client.post(f"/api/friends/request/{target_id}", headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "request_id" in data
        assert "sent" in data["message"].lower()

    def test_cannot_send_request_to_self(self, client, auth_headers):
        """Sending a friend request to yourself returns 400."""
        me_res = client.get("/api/auth/me", headers=auth_headers)
        my_id = me_res.json()["id"]
        res = client.post(f"/api/friends/request/{my_id}", headers=auth_headers)
        assert res.status_code == 400

    def test_cannot_send_duplicate_request(self, client, auth_headers):
        """Sending a duplicate request returns 400."""
        reg = register_user(client, "dup_target", "dup_target@example.com", "SecurePass123")
        target_id = reg.json()["user"]["id"]
        client.post(f"/api/friends/request/{target_id}", headers=auth_headers)
        res = client.post(f"/api/friends/request/{target_id}", headers=auth_headers)
        assert res.status_code == 400

    def test_request_appears_in_incoming(self, client):
        """Sent request appears in receiver's pending list."""
        sender_headers = get_auth_headers(client, "sender_u", "sender@example.com", "SecurePass123")
        receiver_headers = get_auth_headers(client, "receiver_u", "receiver@example.com", "SecurePass123")

        # Get receiver's ID
        rec_me = client.get("/api/auth/me", headers=receiver_headers)
        receiver_id = rec_me.json()["id"]

        # Send request
        client.post(f"/api/friends/request/{receiver_id}", headers=sender_headers)

        # Receiver checks pending
        res = client.get("/api/friends/requests", headers=receiver_headers)
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_send_request_to_nonexistent_user(self, client, auth_headers):
        """Sending to a fake UUID returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.post(f"/api/friends/request/{fake_id}", headers=auth_headers)
        assert res.status_code == 404


class TestAcceptDeclineRequest:
    def _setup_request(self, client):
        """Helper: create sender + receiver, send a request. Returns (sender_hdrs, receiver_hdrs, req_id)."""
        import uuid as _uuid
        uid = _uuid.uuid4().hex[:6]
        sender_hdrs = get_auth_headers(client, f"sndr{uid}", f"sndr{uid}@ex.com", "SecurePass123")
        receiver_hdrs = get_auth_headers(client, f"rcvr{uid}", f"rcvr{uid}@ex.com", "SecurePass123")

        rec_id = client.get("/api/auth/me", headers=receiver_hdrs).json()["id"]
        send_res = client.post(f"/api/friends/request/{rec_id}", headers=sender_hdrs)
        req_id = send_res.json()["request_id"]
        return sender_hdrs, receiver_hdrs, req_id

    def test_accept_request(self, client):
        """Receiver accepts request → appears in friends list."""
        sender_hdrs, receiver_hdrs, req_id = self._setup_request(client)

        res = client.put(f"/api/friends/request/{req_id}/accept", headers=receiver_hdrs)
        assert res.status_code == 200
        assert "accepted" in res.json()["message"].lower()

        friends_res = client.get("/api/friends", headers=receiver_hdrs)
        assert friends_res.json()["total"] >= 1

    def test_decline_request(self, client):
        """Receiver declines request → not in friends list."""
        sender_hdrs, receiver_hdrs, req_id = self._setup_request(client)

        res = client.put(f"/api/friends/request/{req_id}/decline", headers=receiver_hdrs)
        assert res.status_code == 200
        assert "declined" in res.json()["message"].lower()

        friends_res = client.get("/api/friends", headers=receiver_hdrs)
        assert friends_res.json()["total"] == 0

    def test_sender_cannot_accept_own_request(self, client):
        """Sender cannot accept their own request (wrong receiver)."""
        sender_hdrs, receiver_hdrs, req_id = self._setup_request(client)

        # Sender tries to accept — should get 404 (not their request to accept)
        res = client.put(f"/api/friends/request/{req_id}/accept", headers=sender_hdrs)
        assert res.status_code == 404


class TestRemoveFriend:
    def test_remove_friend(self, client):
        """Accepted friend can be removed."""
        import uuid as _uuid
        uid = _uuid.uuid4().hex[:6]
        user1_hdrs = get_auth_headers(client, f"rm1{uid}", f"rm1{uid}@ex.com", "SecurePass123")
        user2_hdrs = get_auth_headers(client, f"rm2{uid}", f"rm2{uid}@ex.com", "SecurePass123")

        user2_id = client.get("/api/auth/me", headers=user2_hdrs).json()["id"]
        send_res = client.post(f"/api/friends/request/{user2_id}", headers=user1_hdrs)
        req_id = send_res.json()["request_id"]
        client.put(f"/api/friends/request/{req_id}/accept", headers=user2_hdrs)

        # Now remove
        res = client.delete(f"/api/friends/{user2_id}", headers=user1_hdrs)
        assert res.status_code == 200

        # Check friends list is empty again
        friends_res = client.get("/api/friends", headers=user1_hdrs)
        assert friends_res.json()["total"] == 0

    def test_remove_nonexistent_friend(self, client, auth_headers):
        """Removing non-friend returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.delete(f"/api/friends/{fake_id}", headers=auth_headers)
        assert res.status_code == 404
