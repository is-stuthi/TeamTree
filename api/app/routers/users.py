"""Profile and skill endpoints. SQL lives in app/queries/users.py."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, current_user, hash_password, verify_password
from app.errors import ApiError
from app.graph import sync
from app.models.common import Message
from app.models.users import (LevelIn, PasswordChange, ProfilePatch, SkillLevelIn, UserMe,
                              UserPublic, UserSkillOut)
from app.queries import users as q

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMe)
async def get_me(user: CurrentUser = Depends(current_user)):
    return await db.fetch_one(q.ME, (user.id,))


@router.patch("/me", response_model=UserMe)
async def update_me(body: ProfilePatch, user: CurrentUser = Depends(current_user)):
    changes = body.model_dump(exclude_unset=True)
    if changes:
        await db.execute(q.profile_update(list(changes)), (*changes.values(), user.id))
        await sync.upsert_user(user.id)
    return await db.fetch_one(q.ME, (user.id,))


@router.put("/me/password", response_model=Message)
async def change_password(body: PasswordChange, user: CurrentUser = Depends(current_user)):
    row = await db.fetch_one(q.PASSWORD_HASH, (user.id,))
    if not verify_password(body.current_password, row["password_hash"]):
        raise ApiError(400, "WRONG_PASSWORD", "Current password is incorrect")
    await db.execute(q.SET_PASSWORD, (hash_password(body.new_password), user.id))
    return Message(message="Password updated")


@router.post("/me/deactivate", response_model=Message)
async def deactivate_me(user: CurrentUser = Depends(current_user)):
    await db.call_proc("deactivate_user", user.id, user.id)       # D4 [SOFT DELETE]
    await sync.delete_user(user.id)
    return Message(message="Account deactivated")


@router.get("/me/skills", response_model=list[UserSkillOut])
async def my_skills(user: CurrentUser = Depends(current_user)):
    return await db.fetch_all(q.SKILLS, (user.id,))


@router.put("/me/skills", response_model=list[UserSkillOut])
async def add_skills(body: list[SkillLevelIn], user: CurrentUser = Depends(current_user)):
    if body:
        rows = ", ".join(["(%s, %s, %s)"] * len(body))
        params = [v for s in body for v in (user.id, s.s_id, s.level)]
        await db.execute(q.BULK_UPSERT_SKILLS.format(rows=rows), params)
        await sync.upsert_user_skills(user.id)
    return await db.fetch_all(q.SKILLS, (user.id,))


@router.put("/me/skills/{s_id}", response_model=list[UserSkillOut])
async def set_skill(s_id: int, body: LevelIn, user: CurrentUser = Depends(current_user)):
    await db.execute(q.UPSERT_SKILL, (user.id, s_id, body.level))
    await sync.upsert_user_skills(user.id)
    return await db.fetch_all(q.SKILLS, (user.id,))


@router.delete("/me/skills/{s_id}", response_model=list[UserSkillOut])
async def remove_skill(s_id: int, user: CurrentUser = Depends(current_user)):
    if not await db.execute(q.DELETE_SKILL, (user.id, s_id)):
        raise ApiError(404, "SKILL_NOT_ON_PROFILE")
    await sync.upsert_user_skills(user.id)
    return await db.fetch_all(q.SKILLS, (user.id,))


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, _: CurrentUser = Depends(current_user)):
    row = await db.fetch_one(q.PUBLIC, (user_id,))
    if row is None:
        raise ApiError(404, "USER_NOT_FOUND")
    return {**row, "skills": await db.fetch_all(q.SKILLS, (user_id,))}
