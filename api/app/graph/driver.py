"""Neo4j async driver singleton. Neo4j being down must never break MySQL features."""
import logging
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase

from app.settings import get_settings

log = logging.getLogger(__name__)
_driver: AsyncDriver | None = None


async def init_driver() -> None:
    global _driver
    s = get_settings()
    _driver = AsyncGraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))


async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def run(query: str, **params: Any) -> list[dict]:
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialised")
    records, _, _ = await _driver.execute_query(query, params, database_="neo4j")
    return [r.data() for r in records]


async def ping() -> bool:
    try:
        return (await run("RETURN 1 AS ok"))[0]["ok"] == 1
    except Exception as e:  # noqa: BLE001 - health check only
        log.warning("neo4j ping failed: %s", e)
        return False
