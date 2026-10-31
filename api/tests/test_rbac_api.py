"""P1: admin vs member at the API layer (the DB layer is covered by test_rbac_db.py)."""
from helpers import login


async def test_member_forbidden_on_admin_routes(client):
    h = await login(client, "bob@teamtree.dev")
    assert (await client.get("/admin/users", headers=h)).status_code == 403
    r = await client.post("/admin/skills", headers=h, json={"s_name": "Rust"})
    assert r.status_code == 403 and r.json()["code"] == "FORBIDDEN_ROLE"


async def test_admin_creates_skill_and_duplicates_are_normalised(client):
    h = await login(client, "admin@teamtree.dev")
    r = await client.post("/admin/skills", headers=h, json={"s_name": "Rust", "category": "Programming"})
    assert r.status_code == 201 and r.json()["s_name"] == "Rust"
    dup = await client.post("/admin/skills", headers=h, json={"s_name": "  rust "})
    assert dup.status_code == 409 and dup.json()["code"] == "SKILL_EXISTS"


async def test_role_change_takes_effect_immediately(client):
    admin = await login(client, "admin@teamtree.dev")
    bob = await login(client, "bob@teamtree.dev")
    r = await client.put("/admin/users/3/role", headers=admin, json={"role": "admin"})
    assert r.status_code == 200 and r.json()["role"] == "admin"
    assert (await client.get("/admin/users", headers=bob)).status_code == 200   # same token, new role
    await client.put("/admin/users/3/role", headers=admin, json={"role": "member"})
    assert (await client.get("/admin/users", headers=bob)).status_code == 403


async def test_last_admin_cannot_be_demoted(client):
    admin = await login(client, "admin@teamtree.dev")
    assert (await client.put("/admin/users/14/role", headers=admin, json={"role": "member"})).status_code == 200
    r = await client.put("/admin/users/1/role", headers=admin, json={"role": "member"})
    assert r.status_code == 409 and r.json()["code"] == "LAST_ADMIN"
    await client.put("/admin/users/14/role", headers=admin, json={"role": "admin"})


async def test_ui_specs_are_public(client):
    names = (await client.get("/ui-schemas")).json()
    assert {"login", "register", "profile_edit", "skill_add", "skill_admin"} <= set(names)
    spec = (await client.get("/ui-schemas/skill_add")).json()
    assert spec["submit"] == {"method": "PUT", "path": "/users/me/skills/{s_id}"}
    assert spec["schema"]["properties"]["level"]["enum"][0] == "Beginner"
