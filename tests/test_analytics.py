def _token(client):
    client.post("/auth/register", json={"email": "ana@example.com", "password": "StrongPass123!"})
    r = client.post("/auth/token", data={"username": "ana@example.com", "password": "StrongPass123!"})
    return r.json()["access_token"]


def test_analytics_owner(client):
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/x", "custom_code": "ana1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get("/analytics/ana1", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["short_code"] == "ana1"
    assert "original_url" in data
    assert "total_clicks" in data
    assert "clicks_last_7_days" in data
    assert "clicks_last_30_days" in data
    assert "recent_clicks" in data


def test_analytics_non_owner(client):
    token1 = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/y", "custom_code": "ana2"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    client.post("/auth/register", json={"email": "other2@example.com", "password": "StrongPass123!"})
    r2 = client.post("/auth/token", data={"username": "other2@example.com", "password": "StrongPass123!"})
    token2 = r2.json()["access_token"]
    r = client.get("/analytics/ana2", headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 403
