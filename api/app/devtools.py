"""Dev-only seed reset behind POST /admin/dev/reset.

Re-applies db/*.sql + seed as root (the same path the tests and scripts/migrate.py
use) and rebuilds the Neo4j projection. Refused unless APP_ENV=development, and the
route is admin-only on top of that. Never reachable in production."""
import asyncio
import logging
import sys
from pathlib import Path

from app import db
from app.graph import driver
from app.graph.sync import full_sync
from app.settings import ROOT

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import graph_init  # noqa: E402
import migrate  # noqa: E402

log = logging.getLogger(__name__)
SEED_GRAPH = ROOT / "graph" / "seed_graph.cypher"


async def reset_seed() -> dict[str, str]:
    await asyncio.to_thread(migrate.apply, quiet=True)
    # 007_rbac re-issues every grant; recycle the pools so no session keeps old state.
    await db.close_pool()
    await db.init_pool()
    try:
        await asyncio.to_thread(graph_init.apply, True, True)
        await full_sync()
        for stmt in graph_init.statements(SEED_GRAPH.read_text(encoding="utf-8")):
            await driver.run(stmt)
        graph = "ok"
    except Exception as e:  # noqa: BLE001 - MySQL reset still counts; full sync repairs later
        log.warning("dev reset: graph rebuild failed: %s", e)
        graph = "unavailable"
    return {"mysql": "ok", "graph": graph}
