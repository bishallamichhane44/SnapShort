import pytest


def _token(client):
    client.post("/auth/register", json={"email": "links@example.com", "password": "StrongPass123!"})
    r = client.post("/auth/token", data={"username": "links@example.com", "password": "StrongPass123!"})
    return r.json()["access_token"]


def test_create_link_authenticated(client):
    token = _token(client)
    r = client.post(
        "/links",
        json={"original_url": "https://www.example.com/long"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["original_url"] == "https://www.example.com/long"
    assert "short_code" in data
    assert "short_url" in data
    assert data["click_count"] == 0


def test_create_link_unauthenticated(client):
    r = client.post("/links", json={"original_url": "https://www.example.com/long"})
    assert r.status_code == 401


def test_create_link_invalid_url(client):
    token = _token(client)
    r = client.post(
        "/links",
        json={"original_url": "javascript:alert(1)"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


def test_create_link_custom_code(client):
    token = _token(client)
    r = client.post(
        "/links",
        json={"original_url": "https://example.com", "custom_code": "mylink"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    assert r.json()["short_code"] == "mylink"


def test_create_link_custom_code_collision(client):
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/a", "custom_code": "same"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.post(
        "/links",
        json={"original_url": "https://example.com/b", "custom_code": "same"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409
    assert "already taken" in r.json()["detail"].lower()


def test_list_links_authenticated(client):
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get("/links", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert "links" in data
    assert data["total"] >= 1
    assert data["page"] == 1
    assert data["limit"] == 20


def test_delete_link_owner(client):
    token = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/del", "custom_code": "todel"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.delete("/links/todel", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204


def test_delete_link_not_found(client):
    token = _token(client)
    r = client.delete("/links/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404


def test_delete_link_non_owner(client):
    token1 = _token(client)
    client.post(
        "/links",
        json={"original_url": "https://example.com/own", "custom_code": "owned"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    client.post("/auth/register", json={"email": "other@example.com", "password": "StrongPass123!"})
    r2 = client.post("/auth/token", data={"username": "other@example.com", "password": "StrongPass123!"})
    token2 = r2.json()["access_token"]
    r = client.delete("/links/owned", headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 403
