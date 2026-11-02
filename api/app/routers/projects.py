"""Projects: create (create_project procedure), browse, detail (Q1), edit, close (close_project)."""
import json

from fastapi import APIRouter, Depends, Query

from app import db
from app.auth import CurrentUser, current_user, optional_user
from app.errors import ApiError
from app.graph import sync
from app.models.projects import ProjectCard, ProjectCreate, ProjectDetail, ProjectFilter, ProjectPatch
from app.ownership import require_owner
from app.queries import projects as q

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectCard])
async def list_projects(f: ProjectFilter = Query()):
    rows = await db.fetch_all(q.LISTING, f.model_dump())
    return [q.split_csv(r, "domains", "required_skills") for r in rows]


@router.post("", response_model=ProjectDetail, status_code=201)
async def create_project(body: ProjectCreate, user: CurrentUser = Depends(current_user)):
    # Project, team, owner membership and domains commit together (one procedure).
    (p_id,) = await db.call_proc("create_project", user.id, body.p_name, body.description,
                                 body.deadline, body.max_team_size, json.dumps(body.domains), out=1)
    await sync.upsert_project(p_id)
    return await _detail(p_id, user)


@router.get("/{p_id}", response_model=ProjectDetail)
async def get_project(p_id: int, user: CurrentUser | None = Depends(optional_user)):
    return await _detail(p_id, user)


@router.patch("/{p_id}", response_model=ProjectDetail)
async def update_project(p_id: int, body: ProjectPatch, user: CurrentUser = Depends(current_user)):
    await require_owner(p_id, user)
    changes = body.model_dump(exclude_unset=True)
    domains = changes.pop("domains", None)
    close = changes.get("status") == "Closed"
    if close:
        changes.pop("status")
    # A cleared (null) value on a NOT NULL column means "leave unchanged".
    changes = {k: v for k, v in changes.items() if v is not None or k not in q.NOT_NULL_COLUMNS}
    if changes:
        await db.execute(q.patch(list(changes)), (*changes.values(), p_id))
    if domains is not None:
        await db.call_proc("set_project_domains", p_id, user.id, json.dumps(domains))
    if close:
        await db.call_proc("close_project", p_id, user.id)     # status + D3 + reject pending
    await sync.upsert_project(p_id)
    return await _detail(p_id, user)


async def _detail(p_id: int, user: CurrentUser | None) -> dict:
    row = await db.fetch_one(q.DETAIL, (p_id,))
    if row is None:
        raise ApiError(404, "PROJECT_NOT_FOUND")
    detail = q.split_csv(row, "domains")
    detail["requirements"] = await db.fetch_all(q.REQUIREMENTS, (p_id,))
    if user is not None:
        v = await db.fetch_one(q.VIEWER, {"p": p_id, "u": user.id})
        detail["viewer"] = {"is_owner": row["owner_id"] == user.id, "is_member": bool(v["is_member"]),
                            "pending_application_id": v["pending_application_id"]}
    return detail
