"""Analytics (design doc §11). Numbers come from SQL views/queries only.
View-based reads run as tt_report (read-only analyst role); queries needing
base tables (Domain, Application, Joins, Task) run as tt_app. Users and teams
analytics are admin-only."""
from typing import Any

from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, current_user, require_admin
from app.queries import analytics as q

router = APIRouter(tags=["analytics"])

STATUSES = ("Open", "Ongoing", "Completed", "Closed")


@router.get("/analytics/skills")
async def skills(_: CurrentUser = Depends(current_user)) -> dict[str, Any]:
    return {"demand": await db.report_fetch_all(q.VIEW_SKILL_DEMAND),
            "top_by_category": await db.report_fetch_all(q.VIEW_TOP_BY_CATEGORY)}


@router.get("/analytics/projects")
async def projects(_: CurrentUser = Depends(current_user)) -> dict[str, Any]:
    counts = {r["status"]: r["n"] for r in await db.report_fetch_all(q.VIEW_BY_STATUS)}
    duration = await db.report_fetch_all(q.VIEW_AVG_DURATION)
    return {
        "by_status": {s: counts.get(s, 0) for s in STATUSES},
        "by_status_rows": [{"status": s, "projects": counts.get(s, 0)} for s in STATUSES],
        "by_domain": await db.fetch_all(q.BASE_BY_DOMAIN),
        "approaching_deadlines": await db.report_fetch_all(q.VIEW_APPROACHING),
        "avg_duration_days": duration[0]["days"],
        "no_applications": await db.fetch_all(q.BASE_NO_APPLICATIONS),
    }


@router.get("/analytics/applications")
async def applications(_: CurrentUser = Depends(current_user)) -> dict[str, Any]:
    per_project = await db.report_fetch_all(q.VIEW_APP_SUMMARY)
    totals = {k: sum(int(r[k]) for r in per_project) for k in ("pending", "accepted", "rejected", "withdrawn")}
    decided = totals["accepted"] + totals["rejected"]          # Pending and Withdrawn excluded (§11.5)
    return {
        **totals,
        "acceptance_rate": round(totals["accepted"] / decided, 4) if decided else None,
        "avg_decision_days": (await db.fetch_one(q.BASE_AVG_DECISION_DAYS))["days"],
        "per_project": per_project,
        "timeline": await db.fetch_all(q.BASE_TIMELINE),
    }


@router.get("/analytics/users")
async def users(_: CurrentUser = Depends(require_admin)) -> dict[str, Any]:
    return {"most_active": await db.fetch_all(q.BASE_USER_ACTIVITY)}


@router.get("/analytics/teams")
async def teams(_: CurrentUser = Depends(require_admin)) -> dict[str, Any]:
    sizes = await db.report_fetch_all(q.VIEW_TEAM_SIZES)
    active = [r for r in sizes if r["status"] in ("Open", "Ongoing")]
    return {
        "avg_team_size": round(sum(r["team_size"] for r in active) / len(active), 1) if active else None,
        "largest": sizes[:5],
        "roles": await db.fetch_all(q.BASE_ROLE_DISTRIBUTION),
        "task_progress": await db.report_fetch_all(q.VIEW_TASK_PROGRESS),
    }


@router.get("/users/me/activity")
async def my_activity(user: CurrentUser = Depends(current_user)) -> list[dict[str, Any]]:
    return await db.fetch_all(q.BASE_ACTIVITY_FEED, {"u": user.id})


@router.get("/users/me/insights")
async def my_insights(user: CurrentUser = Depends(current_user)) -> dict[str, Any]:
    """Dashboard charts: weekly activity (Q13) and tasks per project (Q14)."""
    params = {"u": user.id}
    return {"weekly_activity": await db.fetch_all(q.BASE_ACTIVITY_WEEKLY, params),
            "tasks_by_project": await db.fetch_all(q.BASE_TASKS_BY_PROJECT, params)}


@router.get("/public/stats")
async def public_stats() -> dict[str, Any]:
    return await db.fetch_one(q.PUBLIC_TOTALS)
