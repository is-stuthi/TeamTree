"""P3: apply / withdraw / decide, including the atomic accept transaction,
capacity under concurrency, and rollback when membership creation fails."""
import asyncio

from conftest import one
from helpers import login

MSG = {"msg": "I have the skills you need and can start this week."}


async def _apply(client, email, p_id):
    return await client.post(f"/projects/{p_id}/applications", headers=await login(client, email), json=MSG)


async def test_apply_validations(client):
    r = await _apply(client, "harsh@teamtree.dev", 1)
    assert r.status_code == 201 and r.json()["status"] == "Pending"
    cases = [("harsh@teamtree.dev", 1, 409, "DUPLICATE_PENDING"),
             ("alice@teamtree.dev", 1, 422, "SELF_APPLICATION"),
             ("isha@teamtree.dev", 4, 409, "PROJECT_NOT_OPEN"),      # Ongoing
             ("harsh@teamtree.dev", 5, 409, "PROJECT_FULL"),         # 3/3
             ("farhan@teamtree.dev", 3, 409, "ALREADY_MEMBER")]
    for email, p_id, status, code in cases:
        r = await _apply(client, email, p_id)
        assert (r.status_code, r.json()["code"]) == (status, code), (email, p_id)


async def test_reapply_after_rejection_is_allowed(client):
    assert (await _apply(client, "farhan@teamtree.dev", 1)).status_code == 201   # a_id 2 was Rejected


async def test_message_is_validated(client):
    h = await login(client, "dev@teamtree.dev")
    assert (await client.post("/projects/1/applications", headers=h, json={"msg": "hi"})).status_code == 422


async def test_only_owner_sees_and_decides(client):
    bob = await login(client, "bob@teamtree.dev")
    assert (await client.get("/projects/1/applications", headers=bob)).status_code == 403
    r = await client.post("/applications/1/decision", headers=bob, json={"decision": "Accepted"})
    assert r.status_code == 403 and r.json()["code"] == "NOT_OWNER"
    alice = await login(client, "alice@teamtree.dev")
    received = (await client.get("/projects/1/applications", headers=alice, params={"status": "Pending"})).json()
    esha = next(a for a in received if a["a_id"] == 1)
    assert esha["applicant_name"] == "Esha Kulkarni" and {"s_name": "Python", "level": "Beginner"} in esha["skills"]


async def test_reject_creates_no_membership(client, root_conn):
    bob = await login(client, "bob@teamtree.dev")                       # owns P2; Isha's a_id 5 pending
    r = await client.post("/applications/5/decision", headers=bob, json={"decision": "Rejected"})
    assert r.json()["status"] == "Rejected" and r.json()["decision_date"]
    assert one(root_conn, "SELECT COUNT(*) n FROM Joins WHERE t_id=2 AND u_id=10")["n"] == 0
    again = await client.post("/applications/5/decision", headers=bob, json={"decision": "Accepted"})
    assert again.status_code == 409 and again.json()["code"] == "APP_NOT_PENDING"


async def test_accept_adds_member_with_role(client):
    alice = await login(client, "alice@teamtree.dev")
    r = await client.post("/applications/1/decision", headers=alice, json={"decision": "Accepted", "role": "Data Labeller"})
    assert r.json()["status"] == "Accepted"
    esha = await login(client, "esha@teamtree.dev")
    assert (await client.get("/projects/1", headers=esha)).json()["viewer"]["is_member"] is True


async def test_withdraw_rules(client):
    r = await _apply(client, "kavya@teamtree.dev", 10)
    a_id = r.json()["a_id"]
    other = await login(client, "bob@teamtree.dev")
    assert (await client.post(f"/applications/{a_id}/withdraw", headers=other)).json()["code"] == "NOT_APPLICANT"
    kavya = await login(client, "kavya@teamtree.dev")
    assert (await client.post(f"/applications/{a_id}/withdraw", headers=kavya)).json()["status"] == "Withdrawn"
    mine = (await client.get("/users/me/applications", headers=kavya)).json()
    assert any(a["a_id"] == a_id and a["status"] == "Withdrawn" for a in mine)


async def test_concurrent_accepts_cannot_exceed_capacity(client, root_conn):
    owner = await login(client, "dev@teamtree.dev")
    p = (await client.post("/projects", headers=owner, json={"p_name": "Race Test", "max_team_size": 2})).json()
    a1 = (await _apply(client, "esha@teamtree.dev", p["p_id"])).json()["a_id"]
    a2 = (await _apply(client, "isha@teamtree.dev", p["p_id"])).json()["a_id"]
    results = await asyncio.gather(*[
        client.post(f"/applications/{a}/decision", headers=owner, json={"decision": "Accepted"}) for a in (a1, a2)])
    assert sorted(r.status_code for r in results) == [200, 409]
    assert next(r for r in results if r.status_code == 409).json()["code"] == "PROJECT_FULL"
    assert one(root_conn, "SELECT fn_active_member_count(%s) n", (p["p_id"],))["n"] == 2


async def test_failed_membership_rolls_back_acceptance(client, root_conn):
    # Harsh (9) has pending a_id 4 on P2. Make him a member behind the app's back so the
    # Joins insert inside decide_application hits uq_joins_active and the transaction rolls back.
    with root_conn.cursor() as cur:
        cur.execute("INSERT INTO Joins (t_id, u_id, role, join_date) VALUES (2, 9, 'Member', CURDATE())")
    bob = await login(client, "bob@teamtree.dev")
    r = await client.post("/applications/4/decision", headers=bob, json={"decision": "Accepted"})
    assert r.status_code == 409 and r.json()["code"] == "ALREADY_MEMBER"
    assert one(root_conn, "SELECT status, decision_date FROM Application WHERE a_id=4") == \
        {"status": "Pending", "decision_date": None}
