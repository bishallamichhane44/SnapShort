def test_register_success(client):
    r = client.post("/auth/register", json={"email": "user@example.com", "password": "StrongPass123!"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "StrongPass123!"})
    r = client.post("/auth/register", json={"email": "dup@example.com", "password": "OtherPass123!"})
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"].lower()


def test_register_invalid_email(client):
    r = client.post("/auth/register", json={"email": "not-an-email", "password": "StrongPass123!"})
    assert r.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "StrongPass123!"})
    r = client.post("/auth/token", data={"username": "login@example.com", "password": "StrongPass123!"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wrong@example.com", "password": "StrongPass123!"})
    r = client.post("/auth/token", data={"username": "wrong@example.com", "password": "WrongPassword"})
    assert r.status_code == 401
    assert "invalid" in r.json()["detail"].lower()


def test_login_nonexistent_user(client):
    r = client.post("/auth/token", data={"username": "nobody@example.com", "password": "SomePass123!"})
    assert r.status_code == 401
