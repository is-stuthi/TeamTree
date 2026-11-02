"""Neo4j UPDATE / DELETE features (rubric 9): endorsements, curated skill
relations (admin), and re-embedding a project after edits."""
from fastapi import APIRouter, Depends

from app.auth import CurrentUser, current_user, require_admin
from app.errors import ApiError
from app.graph import sync
from app.graph.cypher import SET_PROJECT_EMBEDDING
from app.graph.driver import run
from app.graph.embed import embed_one, project_text
from app.graph.source import project as project_source
from app.models.common import Message
from app.models.graph import EndorseIn, EndorsementSummary, RelationIn, SkillRelation, WeightIn
from app.ownership import require_owner
from app.queries import graph as read_q
from app.queries import graph_write as q

router = APIRouter(prefix="/graph", tags=["graph"])


@router.put("/endorsements", response_model=list[EndorsementSummary])
async def endorse(body: EndorseIn, user: CurrentUser = Depends(current_user)):
    if body.to == user.id:
        raise ApiError(422, "SELF_ENDORSEMENT", "You can't endorse yourself")
    rows = await run(q.ENDORSE, src=user.id, dst=body.to, sid=body.skill_id, weight=body.weight, note=body.note)
    if not rows:
        raise ApiError(409, "NOT_COLLABORATORS", "You can only endorse people you've shared a team with")
    return await run(read_q.ENDORSEMENTS, id=body.to)


@router.delete("/endorsements/{to}/{skill_id}", response_model=list[EndorsementSummary])
async def unendorse(to: int, skill_id: int, user: CurrentUser = Depends(current_user)):
    rows = await run(q.UNENDORSE, src=user.id, dst=to, sid=skill_id)
    if not rows or not rows[0]["deleted"]:
        raise ApiError(404, "ENDORSEMENT_NOT_FOUND")
    return await run(read_q.ENDORSEMENTS, id=to)


@router.put("/skills/{a}/related/{b}", response_model=list[SkillRelation])
async def relate(a: int, b: int, body: WeightIn, _: CurrentUser = Depends(require_admin)):
    if a == b:
        raise ApiError(422, "SAME_SKILL")
    if not await run(q.RELATE, a=a, b=b, weight=body.weight):
        raise ApiError(404, "SKILL_NOT_FOUND")
    return await run(read_q.RELATIONS)


@router.post("/skill-relations", response_model=list[SkillRelation])
async def relate_form(body: RelationIn, admin: CurrentUser = Depends(require_admin)):
    """Form-friendly variant of PUT /graph/skills/{a}/related/{b}."""
    return await relate(body.a, body.b, WeightIn(weight=body.weight), admin)


@router.delete("/skills/{a}/related/{b}", response_model=list[SkillRelation])
async def unrelate(a: int, b: int, _: CurrentUser = Depends(require_admin)):
    rows = await run(q.UNRELATE, a=a, b=b)
    if not rows or not rows[0]["deleted"]:
        raise ApiError(404, "RELATION_NOT_FOUND")
    return await run(read_q.RELATIONS)


@router.post("/projects/{pid}/reembed", response_model=Message)
async def reembed(pid: int, user: CurrentUser = Depends(current_user)):
    await require_owner(pid, user)
    p = await project_source(pid)
    if not await run(SET_PROJECT_EMBEDDING, id=pid, embedding=await embed_one(project_text(p))):
        await sync.upsert_project(pid)          # node missing: project it from MySQL
    return Message(message="Project re-embedded")
