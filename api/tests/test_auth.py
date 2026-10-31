"""P1: registration, login, sessions."""
from helpers import PASSWORD, login

NEW_USER = {"f_name": "Zara", "l_name": "Khan", "email": "Zara@Example.com", "password": "s3cret-pass"}


async def test_register_returns_token_and_member_role(client):
    r = await client.post("/auth/register", json=NEW_USER)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["user"]["email"] == "zara@example.com"          # normalised by register_user
    assert body["user"]["role"] == "member"
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.json()["f_name"] == "Zara"


async def test_duplicate_email_conflict(client):
    r = await client.post("/auth/register", json={**NEW_USER, "email": "alice@teamtree.dev"})
    assert r.status_code == 409 and r.json()["code"] == "EMAIL_TAKEN"


async def test_register_validates_input(client):
    r = await client.post("/auth/register", json={**NEW_USER, "email": "nope", "password": "short"})
    assert r.status_code == 422


async def test_login_wrong_password(client):
    r = await client.post("/auth/login", json={"email": "alice@teamtree.dev", "password": "wrong"})
    assert r.status_code == 401 and r.json()["code"] == "INVALID_CREDENTIALS"


async def test_deactivated_user_cannot_log_in(client):
    r = await client.post("/auth/login", json={"email": "nikhil@teamtree.dev", "password": PASSWORD})
    assert r.status_code == 403 and r.json()["code"] == "USER_INACTIVE"


async def test_protected_route_requires_token(client):
    assert (await client.get("/users/me")).status_code == 401
    bad = await client.get("/users/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert bad.status_code == 401 and bad.json()["code"] == "INVALID_TOKEN"


async def test_self_deactivation_invalidates_session(client):
    headers = await login(client, "zara@example.com", NEW_USER["password"])
    assert (await client.post("/users/me/deactivate", headers=headers)).status_code == 200
    r = await client.get("/users/me", headers=headers)
    assert r.status_code == 401 and r.json()["code"] == "USER_INACTIVE"
