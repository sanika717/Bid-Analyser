from fastapi.testclient import TestClient

from app.main import app


def test_login_and_protected_routes():
    client = TestClient(app)

    resp = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]

    protected = client.get(
        "/api/status/not-a-real-job",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert protected.status_code == 404
