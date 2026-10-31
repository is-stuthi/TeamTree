"""Apply / withdraw / decide. Every write is a stored procedure call, so the
rules (Open project, no self-apply, one pending, owner-only, capacity, atomic
accept + membership) are enforced by MySQL itself (design doc 16.1-16.2)."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, current_user
from app.errors import ApiError
from app.graph import sync
from app.models.applications import (AppStatus, ApplicationCreate, ApplicationOut, Decision,
                                     ReceivedApplication)
from app.ownership import require_owner
from app.queries import applications as q

router = APIRouter(tags=["applications"])


async def _one(a_id: int) -> dict:
    row = await db.fetch_one(q.ONE, (a_id,))
    if row is None:
        raise ApiError(404, "APP_NOT_FOUND")
    return row


@router.post("/projects/{p_id}/applications", response_model=ApplicationOut, status_code=201)
async def apply(p_id: int, body: ApplicationCreate, user: CurrentUser = Depends(current_user)):
    (a_id,) = await db.call_proc("apply_to_project", user.id, p_id, body.msg.strip(), out=1)
    return await _one(a_id)


@router.get("/projects/{p_id}/applications", response_model=list[ReceivedApplication])
async def received(p_id: int, status: AppStatus | None = None, user: CurrentUser = Depends(current_user)):
    await require_owner(p_id, user)
    rows = await db.fetch_all(q.RECEIVED, {"p": p_id, "status": status})
    return [q.parse_skills(r) for r in rows]


@router.get("/users/me/applications", response_model=list[ApplicationOut])
async def mine(user: CurrentUser = Depends(current_user)):
    return await db.fetch_all(q.MINE, (user.id,))


@router.post("/applications/{a_id}/decision", response_model=ApplicationOut)
async def decide(a_id: int, body: Decision, user: CurrentUser = Depends(current_user)):
    await db.call_proc("decide_application", a_id, user.id, body.decision, body.role)
    app = await _one(a_id)
    if body.decision == "Accepted":
        await sync.upsert_membership(app["p_id"])
    return app


@router.post("/applications/{a_id}/withdraw", response_model=ApplicationOut)
async def withdraw(a_id: int, user: CurrentUser = Depends(current_user)):
    await db.call_proc("withdraw_application", a_id, user.id)
    return await _one(a_id)
