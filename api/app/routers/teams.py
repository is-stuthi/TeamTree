"""Team membership (history kept), leaving, removal and ownership transfer.
All membership writes are stored procedures (remove_member, leave_team,
transfer_ownership) that check the actor inside the database."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, current_user
from app.graph import sync
from app.models.common import Message
from app.models.teams import MyTeam, TeamMember, TopContributor, TransferIn
from app.ownership import require_member
from app.queries import teams as q

router = APIRouter(tags=["teams"])


@router.get("/projects/{p_id}/team", response_model=list[TeamMember])
async def team(p_id: int, include_past: bool = False, user: CurrentUser = Depends(current_user)):
    await require_member(p_id, user)                 # member list includes emails: team only
    return await db.fetch_all(q.MEMBERS, {"p": p_id, "past": include_past})


@router.get("/projects/{p_id}/team/top-contributors", response_model=list[TopContributor])
async def top_contributors(p_id: int, user: CurrentUser = Depends(current_user)):
    await require_member(p_id, user)
    return await db.fetch_all(q.TOP_CONTRIBUTORS, (p_id,))


@router.delete("/projects/{p_id}/team/{user_id}", response_model=list[TeamMember])
async def remove_member(p_id: int, user_id: int, user: CurrentUser = Depends(current_user)):
    await db.call_proc("remove_member", p_id, user.id, user_id)   # owner/admin; unassigns open tasks
    await sync.deactivate_membership(p_id, user_id)
    return await db.fetch_all(q.MEMBERS, {"p": p_id, "past": True})


@router.post("/projects/{p_id}/team/leave", response_model=Message)
async def leave(p_id: int, user: CurrentUser = Depends(current_user)):
    await db.call_proc("leave_team", p_id, user.id)
    await sync.deactivate_membership(p_id, user.id)
    return Message(message="You left the team")


@router.post("/projects/{p_id}/transfer", response_model=list[TeamMember])
async def transfer(p_id: int, body: TransferIn, user: CurrentUser = Depends(current_user)):
    await db.call_proc("transfer_ownership", p_id, user.id, body.new_owner)
    await sync.upsert_project(p_id)
    return await db.fetch_all(q.MEMBERS, {"p": p_id, "past": False})


@router.get("/users/me/teams", response_model=list[MyTeam])
async def my_teams(user: CurrentUser = Depends(current_user)):
    return await db.fetch_all(q.MY_TEAMS, {"u": user.id})
