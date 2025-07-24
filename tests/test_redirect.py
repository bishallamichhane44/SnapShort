def _token(client):
    client.post("/auth/register", json={"email": "redir@example.com", "password": "StrongPass123!"})
    r = client.post("/auth/token", data={"username": "redir@example.com", "password": "StrongPass123!"})
    return r.json()["access_token"]


def test_redirect_valid_code(client):
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/target", "custom_code": "abc123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get("/abc123", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "https://example.com/target"


def test_redirect_nonexistent_code(client):
    r = client.get("/nonexistentcode")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_redirect_expired_link(client):
    import boto3
    from app.config import settings
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/exp", "custom_code": "expired", "expires_in_days": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    table = boto3.resource("dynamodb", region_name="us-east-1").Table(settings.DYNAMODB_TABLE_NAME)
    table.put_item(
        Item={
            "short_code": "expired",
            "original_url": "https://example.com/exp",
            "user_id": "any",
            "created_at": "2026-01-01T00:00:00.000Z",
            "expires_at": 1,
            "click_count": 0,
        }
    )
    r = client.get("/expired", follow_redirects=False)
    assert r.status_code == 410
    assert "expired" in r.json()["detail"].lower()


def test_redirect_increments_click_count(client):
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/count", "custom_code": "cnt"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.get("/cnt", follow_redirects=False)
    client.get("/cnt", follow_redirects=False)
    r = client.get("/analytics/cnt", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["total_clicks"] >= 2
