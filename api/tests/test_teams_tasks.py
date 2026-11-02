"""P4: team history, removal/leave, ownership transfer, tasks, Q5 and Q8."""
from conftest import one
from helpers import login

MSG = {"msg": "Back again: I can finish the scanner screen this sprint."}


async def test_task_tree_recursive_cte(client):
    dev = await login(client, "dev@teamtree.dev")
    tree = (await client.get("/projects/4/tasks/tree", headers=dev)).json()
    by_id = {t["task_id"]: t for t in tree}
    assert [t["task_id"] for t in tree] == [1, 2, 3, 4, 5, 6]          # depth-first order
    assert (by_id[1]["depth"], by_id[2]["depth"], by_id[3]["depth"]) == (0, 1, 2)
    assert by_id[3]["path"] == "Build MVP › Template engine › Markdown parser"


async def test_top_contributors_correlated(client):
    dev = await login(client, "dev@teamtree.dev")
    # P4: 1 Done task (Gauri) over 3 active members -> average 1/3; only Gauri is above it.
    top = (await client.get("/projects/4/team/top-contributors", headers=dev)).json()
    assert top == [{"u_id": 8, "member_name": "Gauri Shetty", "done": 1}]


async def test_tasks_are_members_only(client):
    bob = await login(client, "bob@teamtree.dev")
    r = await client.get("/projects/4/tasks", headers=bob)
    assert r.status_code == 403 and r.json()["code"] == "NOT_MEMBER"


async def test_task_validation(client):
    dev = await login(client, "dev@teamtree.dev")
    r = await client.post("/tasks/4/assign", headers=dev, json={"u_id": 11})
    assert (r.status_code, r.json()["code"]) == (409, "ASSIGNEE_NOT_MEMBER")
    r = await client.post("/projects/4/tasks", headers=dev, json={"t_name": "Late", "due_date": "2099-01-01"})
    assert (r.status_code, r.json()["code"]) == (409, "TASK_AFTER_DEADLINE")
    r = await client.post("/projects/4/tasks", headers=dev, json={"t_name": "Wrong parent", "parent_task_id": 7})
    assert (r.status_code, r.json()["code"]) == (422, "PARENT_OTHER_PROJECT")


async def test_create_assign_and_update_task(client):
    dev = await login(client, "dev@teamtree.dev")
    r = await client.post("/projects/4/tasks", headers=dev,
                          json={"t_name": "Dark theme", "parent_task_id": 4, "u_id": 9, "priority": "Low"})
    assert r.status_code == 201, r.text
    t = r.json()
    assert (t["assignee_name"], t["parent_task_id"]) == ("Harsh Patil", 4)
    harsh = await login(client, "harsh@teamtree.dev")
    r = await client.patch(f"/tasks/{t['task_id']}", headers=harsh, json={"status": "In Progress"})
    assert r.json()["status"] == "In Progress"
    mine = (await client.get("/users/me/tasks", headers=harsh)).json()
    assert any(m["task_id"] == t["task_id"] and m["p_name"] == "Developer Portfolio Generator" for m in mine)


async def test_remove_member_keeps_history_and_unassigns_open_tasks(client, root_conn):
    dev = await login(client, "dev@teamtree.dev")
    r = await client.delete("/projects/4/team/8", headers=dev)              # remove Gauri
    gauri = next(m for m in r.json() if m["u_id"] == 8)
    assert gauri["is_active"] is False and gauri["leave_date"] is not None   # row kept
    tasks = {x["task_id"]: x["u_id"] for x in _rows(root_conn, "SELECT task_id, u_id FROM Task WHERE task_id IN (2, 3)")}
    assert tasks == {2: None, 3: 8}                                          # open unassigned, Done kept


async def test_owner_cannot_be_removed_or_leave(client):
    dev = await login(client, "dev@teamtree.dev")
    r = await client.delete("/projects/4/team/5", headers=dev)
    assert (r.status_code, r.json()["code"]) == (409, "OWNER_CANNOT_LEAVE")
    r = await client.post("/projects/4/team/leave", headers=dev)
    assert r.json()["code"] == "OWNER_CANNOT_LEAVE"


async def test_member_can_leave(client):
    harsh = await login(client, "harsh@teamtree.dev")
    assert (await client.post("/projects/4/team/leave", headers=harsh)).status_code == 200
    teams = (await client.get("/users/me/teams", headers=harsh)).json()
    assert 4 not in {t["p_id"] for t in teams}


async def test_rejoining_creates_a_second_membership_row(client, root_conn):
    chitra = await login(client, "chitra@teamtree.dev")
    await client.delete("/projects/3/team/7", headers=chitra)                # remove Farhan
    farhan = await login(client, "farhan@teamtree.dev")
    a = (await client.post("/projects/3/applications", headers=farhan, json=MSG)).json()
    r = await client.post(f"/applications/{a['a_id']}/decision", headers=chitra, json={"decision": "Accepted"})
    assert r.status_code == 200
    rows = _rows(root_conn, "SELECT leave_date FROM Joins WHERE t_id = 3 AND u_id = 7 ORDER BY j_id")
    assert len(rows) == 2 and rows[0]["leave_date"] is not None and rows[1]["leave_date"] is None


async def test_transfer_ownership(client, root_conn):
    alice = await login(client, "alice@teamtree.dev")                       # owns P9 (Chitra, Liam members)
    r = await client.post("/projects/9/transfer", headers=alice, json={"new_owner": 11})
    assert (r.status_code, r.json()["code"]) == (409, "NOT_ACTIVE_MEMBER")
    r = await client.post("/projects/9/transfer", headers=alice, json={"new_owner": 13})
    roles = {m["u_id"]: m["role"] for m in r.json()}
    assert roles[13] == "Owner" and roles[2] == "Member"
    assert one(root_conn, "SELECT owner_id FROM Project WHERE p_id = 9")["owner_id"] == 13
    assert one(root_conn, "SELECT COUNT(*) n FROM Ownership_Transfer WHERE p_id = 9 AND from_user = 2 AND to_user = 13")["n"] == 1
    r = await client.post("/projects/9/transfer", headers=alice, json={"new_owner": 2})
    assert r.json()["code"] == "NOT_OWNER"                                   # Alice is no longer owner


def _rows(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
