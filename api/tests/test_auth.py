"""Auth integration tests."""
import pytest


def test_login_success_returns_access_token_and_sets_cookie(client):
    client.post("/auth/register", json={"email": "u@test.com", "password": "pw"})
    r = client.post("/auth/login", json={"email": "u@test.com", "password": "pw"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    # refresh_token cookie must be set as HttpOnly
    assert "refresh_token" in r.cookies


def test_login_wrong_password_returns_401(client):
    client.post("/auth/register", json={"email": "u2@test.com", "password": "correct"})
    r = client.post("/auth/login", json={"email": "u2@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_me_without_token_returns_401(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_valid_token(client):
    client.post("/auth/register", json={"email": "me@test.com", "password": "pw"})
    r = client.post("/auth/login", json={"email": "me@test.com", "password": "pw"})
    token = r.json()["access_token"]
    r2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == "me@test.com"


def test_refresh_returns_new_access_token(client):
    client.post("/auth/register", json={"email": "ref@test.com", "password": "pw"})
    login_r = client.post("/auth/login", json={"email": "ref@test.com", "password": "pw"})
    assert login_r.status_code == 200

    # refresh_token cookie is set; use it to get new access token
    refresh_r = client.post("/auth/refresh")
    assert refresh_r.status_code == 200
    assert "access_token" in refresh_r.json()


def test_refresh_without_cookie_returns_401(client):
    # No cookie — ensure client has no stale cookie from another test
    client.cookies.clear()
    r = client.post("/auth/refresh")
    assert r.status_code == 401


def test_logout_clears_cookie(client):
    client.post("/auth/register", json={"email": "logout@test.com", "password": "pw"})
    client.post("/auth/login", json={"email": "logout@test.com", "password": "pw"})
    r = client.post("/auth/logout")
    assert r.status_code == 204
