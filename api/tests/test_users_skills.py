"""P1: profile edits and skill DML (D1 multi-row upsert, D5 delete, D6 upsert)."""
from helpers import login


async def test_profile_patch_updates_allowed_columns(client):
    h = await login(client, "bob@teamtree.dev")
    r = await client.patch("/users/me", headers=h, json={"bio": "New bio", "availability": "Weekends"})
    assert r.status_code == 200
    assert (r.json()["bio"], r.json()["availability"]) == ("New bio", "Weekends")


async def test_profile_patch_ignores_role(client):
    h = await login(client, "bob@teamtree.dev")
    r = await client.patch("/users/me", headers=h, json={"role": "admin"})
    assert r.status_code == 200 and r.json()["role"] == "member"


async def test_skill_upsert_bulk_and_delete(client):
    h = await login(client, "esha@teamtree.dev")
    r = await client.put("/users/me/skills", headers=h,
                         json=[{"s_id": 11, "level": "Beginner"}, {"s_id": 1, "level": "Intermediate"}])
    levels = {s["s_name"]: s["u_s_level"] for s in r.json()}
    assert levels["SQL"] == "Beginner" and levels["Python"] == "Intermediate"   # Python upgraded (D1)

    r = await client.put("/users/me/skills/11", headers=h, json={"level": "Advanced"})   # D6
    assert {s["s_name"]: s["u_s_level"] for s in r.json()}["SQL"] == "Advanced"

    r = await client.delete("/users/me/skills/11", headers=h)                          # D5
    assert "SQL" not in {s["s_name"] for s in r.json()}
    assert (await client.delete("/users/me/skills/11", headers=h)).status_code == 404


async def test_unknown_skill_is_invalid_reference(client):
    h = await login(client, "esha@teamtree.dev")
    r = await client.put("/users/me/skills/999", headers=h, json={"level": "Beginner"})
    assert r.status_code == 422 and r.json()["code"] == "INVALID_REFERENCE"


async def test_public_profile_and_catalogue(client):
    h = await login(client, "esha@teamtree.dev")
    r = await client.get("/users/11", headers=h)
    assert r.json()["name"] == "Jay Kumar" and "Docker" in {s["s_name"] for s in r.json()["skills"]}
    skills = (await client.get("/skills", params={"q": "py"})).json()
    assert [s["s_name"] for s in skills] == ["Python"]


async def test_password_change(client):
    h = await login(client, "isha@teamtree.dev")
    bad = await client.put("/users/me/password", headers=h,
                           json={"current_password": "nope", "new_password": "another-pass"})
    assert bad.status_code == 400
    ok = await client.put("/users/me/password", headers=h,
                          json={"current_password": "password123", "new_password": "another-pass"})
    assert ok.status_code == 200
    await login(client, "isha@teamtree.dev", "another-pass")
