"""
backend/tests/test_health.py
Tests for the health check endpoint.
"""

def test_health_ok(client):
    """GET /api/health should return 200 with status ok."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["app"] == "LearnWise"
    assert "version" in data
