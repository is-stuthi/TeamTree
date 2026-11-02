"""MySQL -> Neo4j projection sync. Called by routers *after* a MySQL write
commits. Failures are logged and never raised: MySQL is the system of record
and `scripts/sync_graph.py --full` reconciles any drift. Graph-only data
(ENDORSES, RELATED_TO) is never touched here.
"""
import functools
import logging

from app import db
from app.graph import cypher as c
from app.graph import source
from app.graph.driver import run
from app.graph.embed import embed_one, project_text, user_text

log = logging.getLogger(__name__)


def _safe(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            await fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001 - graph sync must not break requests
            log.warning("graph sync %s%s failed: %s", fn.__name__, args, e)
    return wrapper


async def _user(user_id: int) -> None:
    u = await source.user(user_id)
    if u is None:
        return
    if not u["is_active"]:
        await run(c.UPSERT_USER, id=u["id"], name=u["name"], availability=u["availability"],
                  active=False, embedding=None)                 # keep the node for history/ownership edges
        await run(c.DEACTIVATE_USER, id=user_id)
        return
    await run(c.UPSERT_USER, id=u["id"], name=u["name"], availability=u["availability"], active=True,
              embedding=await embed_one(user_text(u) or u["name"]))
    await run(c.REPLACE_USER_SKILLS, id=u["id"],
              skills=[{"s_id": s["s_id"], "level": s["level"]} for s in u["skills"]])


async def _project(p_id: int) -> None:
    p = await source.project(p_id)
    if p is None:
        return
    await run(c.UPSERT_PROJECT, id=p["p_id"], name=p["p_name"], status=p["status"], domains=p["domains"],
              owner=p["owner_id"], embedding=await embed_one(project_text(p)))
    await run(c.REPLACE_REQUIREMENTS, id=p["p_id"],
              reqs=[{"s_id": r["s_id"], "role": r["role"], "level": r["level"], "count": r["count"]} for r in p["reqs"]])


async def _membership(p_id: int) -> None:
    members = await db.fetch_all(source.MEMBERS, (p_id,))
    await run(c.REPLACE_MEMBERS, id=p_id,
              members=[{"u_id": m["u_id"], "role": m["role"], "active": bool(m["active"])} for m in members])
    pairs = await source.pairs_for(sorted({m["u_id"] for m in members}))
    if pairs:
        await run(c.UPSERT_COLLABORATIONS, pairs=pairs)


@_safe
async def upsert_skill(skill_id: int) -> None:
    s = await db.fetch_one(source.SKILL, (skill_id,))
    if s:
        await run(c.UPSERT_SKILL, id=s["s_id"], name=s["s_name"], category=s["category"])


@_safe
async def upsert_user(user_id: int) -> None:
    await _user(user_id)


@_safe
async def upsert_user_skills(user_id: int) -> None:
    await _user(user_id)          # skills change the user's embedding too


@_safe
async def upsert_project(project_id: int) -> None:
    await _project(project_id)
    await _membership(project_id)


@_safe
async def upsert_membership(project_id: int) -> None:
    await _membership(project_id)


@_safe
async def deactivate_membership(project_id: int, user_id: int) -> None:
    await run(c.SET_MEMBER_INACTIVE, p=project_id, u=user_id)


@_safe
async def delete_user(user_id: int) -> None:
    await run(c.DEACTIVATE_USER, id=user_id)


async def full_sync() -> dict:
    """Rebuild the whole projection from MySQL (raises on failure; used by the script/tests)."""
    for s in await db.fetch_all("SELECT s_id FROM Skill"):
        await upsert_skill.__wrapped__(s["s_id"])
    for u in await db.fetch_all("SELECT id FROM Users"):
        await _user(u["id"])
    for p in await db.fetch_all("SELECT p_id FROM Project"):
        await _project(p["p_id"])
        await _membership(p["p_id"])
    return (await run(c.COUNTS))[0]
