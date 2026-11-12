"""POST /admin/dev/reset: admin-only, development-only, and really restores the seed."""
from app.settings import get_settings
from helpers import login


async def test_member_cannot_reset(client):
    r = await client.post("/admin/dev/reset", headers=await login(client, "alice@teamtree.dev"))
    assert r.status_code == 403


async def test_reset_refused_outside_development(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "app_env", "production")
    r = await client.post("/admin/dev/reset", headers=await login(client, "admin@teamtree.dev"))
    assert r.status_code == 403 and r.json()["code"] == "DEV_ONLY"


async def test_reset_restores_seed(client, synced_graph):
    admin = await login(client, "admin@teamtree.dev")
    r = await client.post("/admin/skills", headers=admin, json={"s_name": "Zig", "category": "Languages"})
    assert r.status_code == 201
    r = await client.post("/admin/dev/reset", headers=admin)
    assert r.status_code == 200, r.text
    assert r.json()["mysql"] == "ok"
    names = [s["s_name"] for s in (await client.get("/skills", params={"q": "Zig"})).json()]
    assert "Zig" not in names
    # the API keeps working on the recycled pools
    assert (await client.get("/auth/me", headers=admin)).status_code == 200
