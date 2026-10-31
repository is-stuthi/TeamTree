"""Public skill catalogue. Changes are admin-only (see routers/admin.py)."""
from fastapi import APIRouter

from app import db
from app.models.skills import SkillOut
from app.queries import skills as sql

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
async def list_skills(q: str | None = None, category: str | None = None):
    return await db.fetch_all(sql.LIST, {"q": q or None, "category": category or None})


@router.get("/categories", response_model=list[str])
async def categories():
    return [r["category"] for r in await db.fetch_all(sql.CATEGORIES)]
