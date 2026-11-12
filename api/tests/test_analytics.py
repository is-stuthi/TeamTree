"""P7: analytics numbers match hand-computed seed values; access rules."""
from conftest import sql_error
from helpers import login


async def test_acceptance_rate_excludes_pending_and_withdrawn(client):
    h = await login(client, "bob@teamtree.dev")
    a = (await client.get("/analytics/applications", headers=h)).json()
    # seed: 11 accepted, 3 rejected, 5 pending, 2 withdrawn -> 11 / (11 + 3)
    assert (a["accepted"], a["rejected"], a["pending"], a["withdrawn"]) == (11, 3, 5, 2)
    assert a["acceptance_rate"] == round(11 / 14, 4)


async def test_timeline_is_a_full_30_day_series(client):
    h = await login(client, "bob@teamtree.dev")
    t = (await client.get("/analytics/applications", headers=h)).json()["timeline"]
    assert len(t) == 30 and sum(d["applications"] for d in t) <= 21
    assert all(isinstance(d["applications"], int) for d in t)            # gaps are 0, not missing


async def test_skill_demand_and_supply(client):
    h = await login(client, "bob@teamtree.dev")
    s = (await client.get("/analytics/skills", headers=h)).json()
    by = {r["s_name"]: r for r in s["demand"]}
    assert (by["Python"]["projects_requiring"], by["Python"]["users_possessing"]) == (4, 8)   # P1,P3,P5,P9; 8 holders
    assert (by["React"]["projects_requiring"], by["React"]["users_possessing"]) == (4, 6)
    assert (by["Docker"]["projects_requiring"], by["Docker"]["users_possessing"]) == (2, 3)
    top = [r for r in s["top_by_category"] if r["category"] == "Programming"]
    assert top[0] == {"category": "Programming", "s_name": "Python", "projects_requiring": 4, "rank_in_category": 1}


async def test_project_analytics(client):
    h = await login(client, "bob@teamtree.dev")
    p = (await client.get("/analytics/projects", headers=h)).json()
    assert p["by_status"] == {"Open": 6, "Ongoing": 2, "Completed": 1, "Closed": 1}
    assert [r["p_name"] for r in p["no_applications"]] == ["Accessibility Auditor"]


async def test_users_and_teams_analytics_are_admin_only(client):
    bob = await login(client, "bob@teamtree.dev")
    assert (await client.get("/analytics/users", headers=bob)).status_code == 403
    assert (await client.get("/analytics/teams", headers=bob)).status_code == 403
    admin = await login(client, "admin@teamtree.dev")
    teams = (await client.get("/analytics/teams", headers=admin)).json()
    assert teams["largest"][0]["team_size"] >= teams["largest"][-1]["team_size"]
    users = (await client.get("/analytics/users", headers=admin)).json()["most_active"]
    assert len(users) == 10 and {"applications_submitted", "tasks_completed"} <= set(users[0])


async def test_activity_feed_and_public_stats(client):
    h = await login(client, "farhan@teamtree.dev")
    feed = (await client.get("/users/me/activity", headers=h)).json()
    assert {f["kind"] for f in feed} >= {"application", "team", "task"}
    assert feed == sorted(feed, key=lambda f: f["at"], reverse=True)
    stats = (await client.get("/public/stats")).json()                     # no auth
    assert stats == {"users": 14, "open_projects": 6, "teams": 10, "skills": 25, "people_matched": 11}


async def test_my_insights(client):
    h = await login(client, "alice@teamtree.dev")
    body = (await client.get("/users/me/insights", headers=h)).json()
    weeks = body["weekly_activity"]
    assert len(weeks) == 12 and weeks == sorted(weeks, key=lambda w: w["week"])
    assert all(isinstance(w["activity"], int) for w in weeks)
    tasks = body["tasks_by_project"]
    mine = (await client.get("/users/me/tasks", headers=h)).json()
    assert sum(t["open_tasks"] + t["done_tasks"] for t in tasks) == len(mine)


def test_report_user_cannot_read_base_tables(report_conn):
    assert sql_error(report_conn, "SELECT * FROM Application")[0] == 1142
    assert sql_error(report_conn, "SELECT * FROM Users")[0] == 1142
