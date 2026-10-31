"""Admin-only endpoints. Enforced twice: require_admin here, and fn_is_admin
inside the procedures (create_skill, update_skill, set_user_role, deactivate_user)."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, require_admin
from app.errors import ApiError
from app.graph import sync
from app.models.admin import AdminUserOut, RoleChange
from app.models.skills import SkillCreate, SkillOut, SkillPatch
from app.queries import admin as q
from app.queries import skills as skill_q

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/skills", response_model=SkillOut, status_code=201)
async def create_skill(body: SkillCreate, admin: CurrentUser = Depends(require_admin)):
    (s_id,) = await db.call_proc("create_skill", admin.id, body.s_name, body.category, out=1)
    await sync.upsert_skill(s_id)
    return await db.fetch_one(skill_q.ONE, (s_id,))


@router.patch("/skills/{s_id}", response_model=SkillOut)
async def update_skill(s_id: int, body: SkillPatch, admin: CurrentUser = Depends(require_admin)):
    await db.call_proc("update_skill", admin.id, s_id, body.s_name, body.category)
    await sync.upsert_skill(s_id)
    return await db.fetch_one(skill_q.ONE, (s_id,))


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(_: CurrentUser = Depends(require_admin)):
    return await db.fetch_all(q.USERS)


@router.put("/users/{user_id}/role", response_model=AdminUserOut)
async def set_role(user_id: int, body: RoleChange, admin: CurrentUser = Depends(require_admin)):
    await db.call_proc("set_user_role", admin.id, user_id, body.role)
    return await _user(user_id)


@router.post("/users/{user_id}/deactivate", response_model=AdminUserOut)
async def deactivate(user_id: int, admin: CurrentUser = Depends(require_admin)):
    await db.call_proc("deactivate_user", admin.id, user_id)
    await sync.delete_user(user_id)
    return await _user(user_id)


async def _user(user_id: int) -> dict:
    row = await db.fetch_one(q.USER, (user_id,))
    if row is None:
        raise ApiError(404, "USER_NOT_FOUND")
    return row
