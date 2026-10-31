"""P2: create_project procedure, browse/filter, Q1 detail, owner-only edits,
D2 (INSERT...SELECT copy), D3 (UPDATE...JOIN on close), Q6 recommendations."""
from conftest import one
from helpers import login

NEW = {"p_name": "Study Buddy Matcher", "description": "Pair students by course.",
       "domains": ["Education", " Web ", "Education"], "max_team_size": 4}


async def test_create_project_builds_team_and_owner_membership(client, root_conn):
    h = await login(client, "bob@teamtree.dev")
    r = await client.post("/projects", headers=h, json=NEW)
    assert r.status_code == 201, r.text
    p = r.json()
    assert (p["team_name"], p["team_size"], p["domains"]) == ("Study Buddy Matcher Team", 1, ["Education", "Web"])
    assert p["viewer"]["is_owner"] is True
    row = one(root_conn, "SELECT role FROM TeamMemberDetails WHERE p_id=%s AND u_id=3", (p["p_id"],))
    assert row == {"role": "Owner"}


async def test_deadline_before_creation_is_rejected_by_check(client):
    h = await login(client, "bob@teamtree.dev")
    r = await client.post("/projects", headers=h, json={**NEW, "deadline": "2020-01-01"})
    assert r.status_code == 422 and r.json()["code"] == "CHECK_VIOLATION"


async def test_detail_is_public_with_viewer_context(client):
    anon = (await client.get("/projects/3")).json()
    assert anon["owner_name"] == "Chitra Iyer" and anon["team_size"] == 2
    assert {r["s_name"] for r in anon["requirements"]} == {"Docker", "Python", "React"}
    assert anon["viewer"] == {"is_owner": False, "is_member": False, "pending_application_id": None}
    h = await login(client, "farhan@teamtree.dev")
    assert (await client.get("/projects/3", headers=h)).json()["viewer"]["is_member"] is True
    assert (await client.get("/projects/999")).status_code == 404


async def test_listing_filters(client):
    docker = {p["p_name"] for p in (await client.get("/projects", params={"skill": 16})).json()}
    assert docker == {"Smart Inventory Tracker", "Cyber Range for Students"}
    ongoing = (await client.get("/projects", params={"status": "Ongoing"})).json()
    assert {p["p_id"] for p in ongoing} == {4, 9}
    web = (await client.get("/projects", params={"domain": "Web", "q": "RSVP"})).json()
    assert [p["p_id"] for p in web] == [2]


async def test_only_owner_can_edit_and_owner_id_cannot_change(client):
    farhan = await login(client, "farhan@teamtree.dev")
    r = await client.patch("/projects/3", headers=farhan, json={"p_name": "Hijacked"})
    assert r.status_code == 403 and r.json()["code"] == "NOT_OWNER"
    chitra = await login(client, "chitra@teamtree.dev")
    r = await client.patch("/projects/3", headers=chitra, json={"p_name": "Smart Inventory", "owner_id": 7})
    assert r.json()["p_name"] == "Smart Inventory" and r.json()["owner_id"] == 4


async def test_closing_blocks_unfinished_tasks_and_cannot_reopen(client, root_conn):
    h = await login(client, "chitra@teamtree.dev")
    assert (await client.patch("/projects/3", headers=h, json={"status": "Closed"})).status_code == 200
    statuses = {r["task_id"]: r["status"] for r in _rows(root_conn, "SELECT task_id, status FROM Task WHERE p_id=3")}
    assert statuses == {13: "Done", 14: "Blocked", 15: "Blocked"}            # D3
    r = await client.patch("/projects/3", headers=h, json={"status": "Open"})
    assert r.status_code == 409 and r.json()["code"] == "PROJECT_REOPEN_FORBIDDEN"


async def test_requirements_upsert_delete_and_copy(client):
    h = await login(client, "meera@teamtree.dev")                        # owns P8
    r = await client.put("/projects/8/requirements", headers=h,
                         json={"s_id": 5, "req_role": "Frontend Developer", "p_s_level": "Advanced"})
    assert ("TypeScript", "Advanced") in {(x["s_name"], x["p_s_level"]) for x in r.json()}
    r = await client.delete("/projects/8/requirements/5", headers=h, params={"role": "Frontend Developer"})
    assert "TypeScript" not in {x["s_name"] for x in r.json()}
    r = await client.post("/projects/8/requirements/copy-from/1", headers=h)    # D2
    assert {"Python", "Deep Learning", "React", "UI/UX"} <= {x["s_name"] for x in r.json()}
    bob = await login(client, "bob@teamtree.dev")
    assert (await client.post("/projects/8/requirements/copy-from/1", headers=bob)).status_code == 403


async def test_recommendations_use_correlated_exists(client):
    h = await login(client, "jay@teamtree.dev")
    recs = (await client.get("/users/me/recommended-projects", headers=h, params={"limit": 20})).json()
    assert all(p["status"] == "Open" and p["owner_id"] != 11 for p in recs)
    p1 = next(p for p in recs if p["p_id"] == 1)
    assert p1["matched_requirements"] >= 1 and p1["total_requirements"] == 3


async def test_my_projects_lists_owned_and_member(client):
    h = await login(client, "alice@teamtree.dev")
    mine = (await client.get("/users/me/projects", headers=h)).json()
    assert {(p["p_id"], p["is_owner"]) for p in mine} >= {(1, True), (9, True), (6, False)}
    owned = (await client.get("/users/me/projects", headers=h, params={"owned": True})).json()
    assert all(p["is_owner"] for p in owned)


def _rows(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
