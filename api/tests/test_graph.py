"""P6: Neo4j graph + vector (rubric 4 and 9): sync, reads, updates, deletes."""
import pytest

from conftest import one
from helpers import login

pytestmark = pytest.mark.usefixtures("synced_graph")


async def _graph(query: str, **params):
    from app.graph.driver import run
    return await run(query, **params)


async def test_sync_is_idempotent(client, synced_graph):
    from app.graph.sync import full_sync
    again = await full_sync()
    assert (again["nodes"], again["rels"]) == (synced_graph["nodes"], synced_graph["rels"])


async def test_vector_search_ranks_the_ml_project_first(client):
    r = await client.get("/graph/search/projects", params={"q": "machine learning image classifier"})
    assert r.status_code == 200 and r.json()[0]["name"] == "Plant Disease Classifier"
    similar = (await client.get("/graph/projects/1/similar")).json()
    assert len(similar) == 4 and all(s["id"] != 1 for s in similar)


async def test_network_path_recommendations_related(client):
    h = await login(client, "farhan@teamtree.dev")
    net = (await client.get("/graph/users/7/network", headers=h, params={"depth": 1})).json()
    deg = {n["name"]: n["degree"] for n in net["nodes"]}
    assert deg["Farhan Ali"] == 0 and {deg["Chitra Iyer"], deg["Esha Kulkarni"], deg["Bob Mehta"]} == {1}
    path = (await client.get("/graph/path", headers=h, params={"from": 6, "to": 13})).json()
    assert path["hops"] == 3 and path["path"][0]["id"] == 6 and path["path"][-1]["id"] == 13
    recs = {r["name"] for r in (await client.get("/graph/users/7/recommended-collaborators", headers=h)).json()}
    assert {"Alice Rao", "Liam Dsouza", "Jay Kumar"} <= recs
    rel = (await client.get("/graph/skills/16/related")).json()
    assert "Kubernetes" in {s["name"] for s in rel["curated"]}


async def test_gap_candidates_combine_mysql_gap_and_graph(client):
    chitra = await login(client, "chitra@teamtree.dev")
    rows = (await client.get("/graph/projects/3/gap-candidates", headers=chitra)).json()
    jay = [r for r in rows if r["name"] == "Jay Kumar" and r["skill"] == "Docker"]
    assert jay and any(not r["related"] for r in jay)
    assert all(r["name"] not in {"Chitra Iyer", "Farhan Ali"} for r in rows)      # not current members


async def test_endorse_update_delete(client):
    alice = await login(client, "alice@teamtree.dev")
    body = {"to": 8, "skill_id": 21, "weight": 3, "note": "Lovely UI"}
    r = await client.put("/graph/endorsements", headers=alice, json=body)                     # create
    assert next(e["avg_weight"] for e in r.json() if e["skill"] == "UI/UX") == 3.0
    r = await client.put("/graph/endorsements", headers=alice, json={**body, "weight": 5})       # U
    assert next(e["avg_weight"] for e in r.json() if e["skill"] == "UI/UX") == 5.0
    r = await client.delete("/graph/endorsements/8/21", headers=alice)                         # D
    assert "UI/UX" not in {e["skill"] for e in r.json()}
    assert (await client.delete("/graph/endorsements/8/21", headers=alice)).status_code == 404
    r = await client.put("/graph/endorsements", headers=alice, json={**body, "to": 11})
    assert (r.status_code, r.json()["code"]) == (409, "NOT_COLLABORATORS")
    r = await client.put("/graph/endorsements", headers=alice, json={**body, "to": 2})
    assert r.json()["code"] == "SELF_ENDORSEMENT"


async def test_skill_relations_are_admin_only(client):
    bob = await login(client, "bob@teamtree.dev")
    assert (await client.put("/graph/skills/2/related/4", headers=bob, json={"weight": 0.4})).status_code == 403
    assert (await client.delete("/graph/skills/16/related/17", headers=bob)).status_code == 403
    admin = await login(client, "admin@teamtree.dev")
    r = await client.put("/graph/skills/2/related/4", headers=admin, json={"weight": 0.4})
    assert any({x["a"], x["b"]} == {2, 4} and x["weight"] == 0.4 for x in r.json())
    r = await client.delete("/graph/skills/2/related/4", headers=admin)
    assert not any({x["a"], x["b"]} == {2, 4} for x in r.json())


async def test_accept_and_remove_update_the_graph(client):
    alice = await login(client, "alice@teamtree.dev")
    await client.post("/applications/1/decision", headers=alice, json={"decision": "Accepted"})   # Esha -> P1
    rows = await _graph("MATCH (:User {id: 6})-[m:MEMBER_OF]->(:Project {id: 1}) RETURN m.active AS a")
    assert rows == [{"a": True}]
    assert await _graph("MATCH (:User {id: 6})-[c:COLLABORATED_WITH]-(:User {id: 2}) RETURN count(c) AS n") == [{"n": 1}]
    dev = await login(client, "dev@teamtree.dev")
    await client.delete("/projects/4/team/9", headers=dev)                                         # remove Harsh
    assert await _graph("MATCH (:User {id: 9})-[m:MEMBER_OF]->(:Project {id: 4}) RETURN m.active AS a") == [{"a": False}]


async def test_neo4j_down_does_not_block_mysql(client, root_conn, monkeypatch):
    from neo4j.exceptions import ServiceUnavailable
    import app.graph.sync as sync_mod

    async def down(*_a, **_k):
        raise ServiceUnavailable("graph is down")

    monkeypatch.setattr(sync_mod, "run", down)
    bob = await login(client, "bob@teamtree.dev")
    r = await client.post("/applications/4/decision", headers=bob, json={"decision": "Accepted"})   # Harsh -> P2
    assert r.status_code == 200                                                    # MySQL committed anyway
    assert one(root_conn, "SELECT fn_is_active_member(2, 9) m")["m"] == 1
    assert await _graph("MATCH (:User {id: 9})-[m:MEMBER_OF]->(:Project {id: 2}) RETURN count(m) AS n") == [{"n": 0}]
    monkeypatch.undo()
    from app.graph.sync import full_sync
    await full_sync()                                                                # reconcile
    assert await _graph("MATCH (:User {id: 9})-[m:MEMBER_OF]->(:Project {id: 2}) RETURN m.active AS a") == [{"a": True}]
