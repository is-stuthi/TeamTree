"""Candidate matching (Q3 / Q4 prefilter + transparent scoring) and the skill gap."""
from fastapi import APIRouter, Depends, Query

from app import db
from app.auth import CurrentUser, current_user
from app.models.matching import CandidateOut, SkillGapRow
from app.ownership import require_member, require_owner
from app.queries import matching as q
from app.services.matching import Candidate, Requirement, score

router = APIRouter(tags=["matching"])


@router.get("/projects/{p_id}/candidates", response_model=list[CandidateOut])
async def candidates(p_id: int, full: bool = False, limit: int = Query(20, ge=1, le=100),
                     user: CurrentUser = Depends(current_user)):
    await require_owner(p_id, user)
    reqs = [Requirement(**r) for r in await db.fetch_all(q.REQUIREMENTS, (p_id,))]
    if not reqs:
        return []
    ids = [r["id"] for r in await db.fetch_all(q.ALL_SKILLS if full else q.ANY_SKILL, {"p": p_id})]
    if not ids:
        return []
    ph = q.placeholders(len(ids))
    profiles = await db.fetch_all(q.PROFILES.format(ids=ph), ids)
    skills: dict[int, dict[int, int]] = {}
    for row in await db.fetch_all(q.SKILLS.format(ids=ph), (*ids, p_id)):
        skills.setdefault(row["u_id"], {})[row["s_id"]] = row["level"]
    domain = {r["u_id"] for r in await db.fetch_all(q.DOMAIN_MATCH.format(ids=ph), (*ids, p_id, p_id))}

    results = []
    for p in profiles:
        c = Candidate(p["experience_level"], p["availability"], skills.get(p["u_id"], {}), p["u_id"] in domain)
        results.append({**p, **score(c, reqs)})
    results.sort(key=lambda r: (-r["score"], r["name"]))
    return results[:limit]


@router.get("/projects/{p_id}/skill-gap", response_model=list[SkillGapRow])
async def skill_gap(p_id: int, user: CurrentUser = Depends(current_user)):
    await require_member(p_id, user)
    return await db.fetch_all(q.SKILL_GAP, (p_id,))
