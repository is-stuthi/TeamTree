"""Regression tests for the P4-P7 code-review findings."""
import re

import pytest

from helpers import login

pytestmark = pytest.mark.usefixtures("synced_graph")


async def _graph(query: str, **params):
    from app.graph.driver import run
    return await run(query, **params)


async def test_timeline_days_are_real_dates(client):
    h = await login(client, "bob@teamtree.dev")
    days = [d["day"] for d in (await client.get("/analytics/applications", headers=h)).json()["timeline"]]
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) for d in days) and len(set(days)) == 30


async def test_team_list_and_skill_gap_are_team_only(client):
    jay = await login(client, "jay@teamtree.dev")                       # not on P5
    assert (await client.get("/projects/5/team", headers=jay)).status_code == 403
    assert (await client.get("/projects/5/skill-gap", headers=jay)).status_code == 403
    assert (await client.get("/graph/projects/5/gap-candidates", headers=jay)).status_code == 403
    farhan = await login(client, "farhan@teamtree.dev")                 # owner of P5
    assert (await client.get("/projects/5/team", headers=farhan)).status_code == 200


async def test_path_to_self_is_zero_hops(client):
    h = await login(client, "bob@teamtree.dev")
    r = await client.get("/graph/path", headers=h, params={"from": 3, "to": 3})
    assert r.status_code == 200 and r.json() == {"path": [{"id": 3, "name": "Bob Mehta"}], "hops": 0}


async def test_related_keeps_curated_and_orders_co_occurring(client):
    r = (await client.get("/graph/skills/16/related")).json()          # Docker
    assert [s["name"] for s in r["curated"]][:1] == ["Kubernetes"]     # highest weight first
    together = [s["together"] for s in r["co_occurring"]]
    assert together == sorted(together, reverse=True) and all(t >= 2 for t in together)


async def test_inactive_users_keep_a_node_for_history(client):
    rows = await _graph("MATCH (u:User {id: 15}) RETURN u.active AS active")
    assert rows == [{"active": False}]                                 # Nikhil is deactivated in the seed


async def test_rejoined_member_is_active_in_graph(client):
    chitra = await login(client, "chitra@teamtree.dev")
    await client.delete("/projects/3/team/7", headers=chitra)           # Farhan leaves...
    farhan = await login(client, "farhan@teamtree.dev")
    a = (await client.post("/projects/3/applications", headers=farhan,
                           json={"msg": "Rejoining to finish the scanner screen."})).json()
    await client.post(f"/applications/{a['a_id']}/decision", headers=chitra, json={"decision": "Accepted"})
    rows = await _graph("MATCH (:User {id: 7})-[m:MEMBER_OF]->(:Project {id: 3}) RETURN m.active AS a")
    assert rows == [{"a": True}]                                       # ...and is active again, one edge


async def test_endorsements_expose_endorser_ids(client):
    h = await login(client, "dev@teamtree.dev")
    e = (await client.get("/graph/users/8/endorsements", headers=h)).json()
    assert any(5 in x["endorser_ids"] for x in e)                      # Dev (5) endorsed Gauri
