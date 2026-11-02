"""Regression tests for the P0-P3 architect/code review fixes."""
from conftest import one, sql_error
from helpers import login


def test_task_update_only_rechecks_changed_columns(app_conn):
    # Gauri (8) leaves P4; her Done task 3 stays assigned to her (history). Editing
    # another column of that task must still work (previously ASSIGNEE_NOT_MEMBER).
    with app_conn.cursor() as cur:
        cur.execute("CALL remove_member(4, 5, 8)")
        assert cur.execute("UPDATE Task SET priority = 'Low' WHERE task_id = 3") == 1
    assert one(app_conn, "SELECT u_id, priority FROM Task WHERE task_id = 3") == {"u_id": 8, "priority": "Low"}
    # ...but re-assigning to a non-member is still rejected.
    assert sql_error(app_conn, "UPDATE Task SET u_id = 11 WHERE task_id = 4") == (1644, "ASSIGNEE_NOT_MEMBER")


def test_task_structure_columns_are_not_updatable(app_conn):
    assert sql_error(app_conn, "UPDATE Task SET p_id = 9 WHERE task_id = 1")[0] == 1143
    assert sql_error(app_conn, "UPDATE Task SET parent_task_id = 7 WHERE task_id = 1")[0] == 1143


def test_task_parent_must_be_in_same_project_and_project_open(app_conn):
    assert sql_error(app_conn, "INSERT INTO Task (p_id, parent_task_id, t_name) VALUES (4, 7, 'x')") == \
        (1644, "PARENT_OTHER_PROJECT")
    assert sql_error(app_conn, "INSERT INTO Task (p_id, t_name) VALUES (7, 'late work')") == (1644, "PROJECT_FINISHED")


def test_routines_and_domain_writes_are_locked_down(app_conn):
    assert sql_error(app_conn, "CALL validate_task(1, NULL, NULL, NULL)")[0] == 1370
    assert sql_error(app_conn, "INSERT INTO Domain (project_id, d_name) VALUES (1, 'Hack')")[0] == 1142


def test_project_edits_stay_consistent_with_team_and_tasks(app_conn):
    assert sql_error(app_conn, "UPDATE Project SET max_team_size = 2 WHERE p_id = 5") == (1644, "CAPACITY_BELOW_TEAM")
    assert sql_error(app_conn, "UPDATE Project SET deadline = CURDATE() + INTERVAL 1 DAY WHERE p_id = 4") == \
        (1644, "DEADLINE_BEFORE_TASKS")


async def test_close_project_is_atomic_and_rejects_pending(client, root_conn):
    dev = await login(client, "dev@teamtree.dev")
    assert (await client.patch("/projects/10", headers=dev, json={"status": "Closed"})).status_code == 403
    liam = await login(client, "liam@teamtree.dev")
    r = await client.patch("/projects/10", headers=liam, json={"status": "Closed"})
    assert r.status_code == 200 and r.json()["status"] == "Closed"
    app = one(root_conn, "SELECT status, decision_date FROM Application WHERE a_id = 17")
    assert app["status"] == "Rejected" and app["decision_date"] is not None


async def test_domains_are_atomic_case_insensitive_and_keep_commas(client):
    h = await login(client, "bob@teamtree.dev")
    r = await client.post("/projects", headers=h,
                          json={"p_name": "Domain Edge Cases", "domains": ["Web", "web", "AI, ML", "  "]})
    assert r.status_code == 201, r.text
    assert sorted(d.lower() for d in r.json()["domains"]) == ["ai, ml", "web"]
    listed = next(p for p in (await client.get("/projects", params={"q": "Domain Edge"})).json())
    assert "AI, ML" in listed["domains"]


async def test_patch_can_clear_optional_fields(client):
    h = await login(client, "kavya@teamtree.dev")
    await client.patch("/users/me", headers=h, json={"bio": "temp", "location": "Kochi"})
    r = await client.patch("/users/me", headers=h, json={"bio": None, "location": None, "f_name": None})
    assert (r.json()["bio"], r.json()["location"], r.json()["f_name"]) == (None, None, "Kavya")


def test_admin_can_remove_a_member(app_conn):
    # Design doc 13.9: an administrator (user 1) may remove members, not only the owner.
    assert one(app_conn, "SELECT fn_is_active_member(9, 13) m")["m"] == 1
    with app_conn.cursor() as cur:
        cur.execute("CALL remove_member(9, 1, 13)")
    assert one(app_conn, "SELECT fn_is_active_member(9, 13) m")["m"] == 0
    assert sql_error(app_conn, "CALL remove_member(9, 3, 4)") == (1644, "NOT_OWNER")   # plain member can't
