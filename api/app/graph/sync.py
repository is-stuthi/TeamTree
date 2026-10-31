"""MySQL -> Neo4j projection sync. Called by routers *after* a MySQL write
commits. Failures are logged and never raised: MySQL is the system of record
and `scripts/sync_graph.py --full` (P6) reconciles any drift.

P1 defines the call sites; the Cypher bodies are filled in during P6.
"""
import functools
import logging

log = logging.getLogger(__name__)


def _safe(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            await fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001 - graph sync must not break requests
            log.warning("graph sync %s%s failed: %s", fn.__name__, args, e)
    return wrapper


@_safe
async def upsert_user(user_id: int) -> None:
    log.debug("sync upsert_user(%s): pending P6", user_id)


@_safe
async def upsert_user_skills(user_id: int) -> None:
    log.debug("sync upsert_user_skills(%s): pending P6", user_id)


@_safe
async def upsert_skill(skill_id: int) -> None:
    log.debug("sync upsert_skill(%s): pending P6", skill_id)


@_safe
async def upsert_project(project_id: int) -> None:
    log.debug("sync upsert_project(%s): pending P6", project_id)


@_safe
async def upsert_membership(project_id: int) -> None:
    log.debug("sync upsert_membership(%s): pending P6", project_id)


@_safe
async def delete_user(user_id: int) -> None:
    log.debug("sync delete_user(%s): pending P6", user_id)
