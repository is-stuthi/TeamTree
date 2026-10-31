"""Project skill requirements (owner only). Includes D2 (INSERT ... SELECT copy)."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, current_user
from app.errors import ApiError
from app.graph import sync
from app.models.requirements import RequirementCopy, RequirementIn, RequirementOut
from app.ownership import project_owner, require_owner
from app.queries import projects as project_q
from app.queries import requirements as q

router = APIRouter(prefix="/projects/{p_id}/requirements", tags=["requirements"])


async def _list(p_id: int) -> list[dict]:
    return await db.fetch_all(project_q.REQUIREMENTS, (p_id,))


@router.get("", response_model=list[RequirementOut])
async def list_requirements(p_id: int):
    await project_owner(p_id)                              # 404 for unknown projects
    return await _list(p_id)


@router.put("", response_model=list[RequirementOut])
async def upsert_requirement(p_id: int, body: RequirementIn, user: CurrentUser = Depends(current_user)):
    await require_owner(p_id, user)
    await db.execute(q.UPSERT, (p_id, body.s_id, body.req_role.strip(), body.p_s_level, body.req_count))
    await sync.upsert_project(p_id)
    return await _list(p_id)


@router.delete("/{s_id}", response_model=list[RequirementOut])
async def delete_requirement(p_id: int, s_id: int, role: str = "Contributor",
                             user: CurrentUser = Depends(current_user)):
    await require_owner(p_id, user)
    if not await db.execute(q.DELETE, (p_id, s_id, role)):
        raise ApiError(404, "REQUIREMENT_NOT_FOUND")
    await sync.upsert_project(p_id)
    return await _list(p_id)


@router.post("/copy-from/{src_p_id}", response_model=list[RequirementOut])
async def copy_requirements(p_id: int, src_p_id: int, user: CurrentUser = Depends(current_user)):
    await require_owner(p_id, user)
    await project_owner(src_p_id)
    if src_p_id == p_id:
        raise ApiError(422, "SAME_PROJECT")
    await db.execute(q.COPY_FROM, (p_id, src_p_id))      # D2
    await sync.upsert_project(p_id)
    return await _list(p_id)


@router.post("/copy", response_model=list[RequirementOut], include_in_schema=True)
async def copy_requirements_body(p_id: int, body: RequirementCopy, user: CurrentUser = Depends(current_user)):
    """Form-friendly variant of copy-from (source chosen in a SchemaForm)."""
    return await copy_requirements(p_id, body.src_p_id, user)
