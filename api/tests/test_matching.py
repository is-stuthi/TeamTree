"""P5: transparent scoring (unit), Q3/Q4 candidate queries, skill gap, Q7."""
from helpers import login
from app.services.matching import Candidate, Requirement, score

REQS = [Requirement(16, "Docker", 3), Requirement(1, "Python", 2), Requirement(6, "React", 2)]


def test_breakdown_sums_to_score_and_weights_apply():
    c = Candidate("Expert", "Full-time", {16: 4, 1: 4, 6: 3}, domain_match=True)
    r = score(c, REQS)
    assert r["breakdown"] == {"coverage": 50.0, "proficiency": 20.0, "experience": 15.0,
                              "domain": 10.0, "availability": 5.0}
    assert r["score"] == 100.0 == round(sum(r["breakdown"].values()), 1)
    assert r["fully_qualified"] and r["missing_skills"] == []


def test_partial_candidate_is_explained():
    c = Candidate("Beginner", "Unavailable", {16: 1})             # Docker, but only Beginner
    r = score(c, REQS)
    assert r["breakdown"]["coverage"] == round(50 / 3, 1)
    assert r["breakdown"]["proficiency"] == round(20 * (1 / 3), 1)  # 1/3 of the required level
    assert r["breakdown"]["availability"] == 0.0
    assert r["missing_skills"] == ["Docker", "Python", "React"]
    assert r["score"] == round(sum(r["breakdown"].values()), 1)


def test_no_required_skills_means_zero_coverage():
    r = score(Candidate("Advanced", "Part-time", {}), REQS)
    assert (r["breakdown"]["coverage"], r["breakdown"]["proficiency"], r["fully_qualified"]) == (0.0, 0.0, False)


def test_proficiency_is_capped_at_required_level():
    r = score(Candidate("Beginner", "Weekends", {16: 4}), [Requirement(16, "Docker", 1)])
    assert r["breakdown"]["proficiency"] == 20.0


async def test_fully_qualified_candidates_use_relational_division(client):
    chitra = await login(client, "chitra@teamtree.dev")
    full = (await client.get("/projects/3/candidates", headers=chitra, params={"full": True})).json()
    assert [c["name"] for c in full] == ["Jay Kumar"]                 # only Jay meets all three
    assert full[0]["fully_qualified"] and full[0]["score"] == round(sum(full[0]["breakdown"].values()), 1)
    anyone = (await client.get("/projects/3/candidates", headers=chitra, params={"limit": 50})).json()
    names = {c["name"] for c in anyone}
    assert "Jay Kumar" in names and len(anyone) > 1
    assert not names & {"Chitra Iyer", "Farhan Ali", "Nikhil Bhat"}  # owner, member, inactive excluded
    assert anyone == sorted(anyone, key=lambda c: (-c["score"], c["name"]))


async def test_candidates_are_owner_only(client):
    farhan = await login(client, "farhan@teamtree.dev")
    assert (await client.get("/projects/3/candidates", headers=farhan)).status_code == 403


async def test_skill_gap_closes_after_accepting_qualified_applicant(client):
    chitra = await login(client, "chitra@teamtree.dev")
    gap = {g["s_name"]: g for g in (await client.get("/projects/3/skill-gap", headers=chitra)).json()}
    assert (gap["Docker"]["qualified_members"], gap["Docker"]["shortfall"]) == (0, 1)
    jay = await login(client, "jay@teamtree.dev")
    a = (await client.post("/projects/3/applications", headers=jay,
                           json={"msg": "I can own Docker and deployment for the tracker."})).json()
    await client.post(f"/applications/{a['a_id']}/decision", headers=chitra, json={"decision": "Accepted"})
    gap = {g["s_name"]: g for g in (await client.get("/projects/3/skill-gap", headers=chitra)).json()}
    assert gap["Docker"]["shortfall"] == 0


async def test_strongest_skill_correlated_subquery(client):
    h = await login(client, "bob@teamtree.dev")
    assert (await client.get("/users/11", headers=h)).json()["strongest_skill"] == "Docker"   # Expert, alphabetical first
