"""The current user's projects and SQL-based recommendations (Q6)."""
from fastapi import APIRouter, Depends, Query

from app import db
from app.auth import CurrentUser, current_user
from app.models.projects import MyProject, RecommendedProject
from app.queries import discovery as q
from app.queries.projects import split_csv

router = APIRouter(prefix="/users/me", tags=["discovery"])


@router.get("/projects", response_model=list[MyProject])
async def my_projects(owned: bool = False, user: CurrentUser = Depends(current_user)):
    rows = await db.fetch_all(q.MY_PROJECTS, {"u": user.id})
    if owned:
        rows = [r for r in rows if r["is_owner"]]
    return [split_csv(r, "domains", "required_skills") for r in rows]


@router.get("/recommended-projects", response_model=list[RecommendedProject])
async def recommended(limit: int = Query(6, ge=1, le=50), user: CurrentUser = Depends(current_user)):
    rows = await db.fetch_all(q.RECOMMENDED, {"u": user.id, "limit": limit})
    return [split_csv(r, "domains", "required_skills") for r in rows]
