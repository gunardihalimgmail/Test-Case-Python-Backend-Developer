# tests/test_auth.py
def test_register_and_login(client):
    # REGISTER
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "secret"})
    assert res.status_code == 200
    tokens = res.json()
    assert "access_token" in tokens

    # LOGIN
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "secret"})
    assert res.status_code == 200
    tokens = res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
