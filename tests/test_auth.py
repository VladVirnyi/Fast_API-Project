import pytest

from app.core.config import get_settings


settings = get_settings()


@pytest.mark.asyncio
async def test_register_and_login_sets_cookie(client):
    register_response = await client.post(
        "/auth/register",
        json={"username": "authuser", "password": "strongpass123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["username"] == "authuser"

    login_response = await client.post(
        "/auth/login",
        json={"username": "authuser", "password": "strongpass123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["message"] == "Login successful"

    set_cookie = login_response.headers.get("set-cookie", "")
    assert settings.auth_cookie_name in set_cookie


@pytest.mark.asyncio
async def test_protected_endpoint_requires_cookie(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_cookie(client):
    await client.post(
        "/auth/register",
        json={"username": "cookieuser", "password": "strongpass123"},
    )
    login_response = await client.post(
        "/auth/login",
        json={"username": "cookieuser", "password": "strongpass123"},
    )
    assert login_response.status_code == 200

    token_value = login_response.cookies.get(settings.auth_cookie_name)
    assert token_value is not None

    me_response = await client.get(
        "/auth/me",
        cookies={settings.auth_cookie_name: token_value},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "cookieuser"