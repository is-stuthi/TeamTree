"""Rebuild the Neo4j projection from MySQL, then load graph-only seed data.

    python scripts/sync_graph.py --full          # reset graph, constraints/indexes, project, seed
    python scripts/sync_graph.py                 # re-project only (keeps endorsements/relations)

The MySQL -> graph projection is idempotent (MERGE): running it twice yields the
same node/relationship counts. --full also wipes graph-only data and reloads
graph/seed_graph.cypher (endorsements, RELATED_TO).
"""
import argparse
import asyncio
import sys
from pathlib import Path

API = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(API), str(API / "scripts")]

import graph_init  # noqa: E402
from app import db  # noqa: E402
from app.graph import driver  # noqa: E402
from app.graph.cypher import COUNTS  # noqa: E402
from app.graph.sync import full_sync  # noqa: E402
from app.settings import ROOT  # noqa: E402

SEED = ROOT / "graph" / "seed_graph.cypher"


async def _run(full: bool, quiet: bool) -> dict:
    await db.init_pool()
    await driver.init_driver()
    try:
        counts = await full_sync()
        if full:
            for stmt in graph_init.statements(SEED.read_text(encoding="utf-8")):
                await driver.run(stmt)
            counts = (await driver.run(COUNTS))[0]
        if not quiet:
            print(f"graph: {counts['nodes']} nodes, {counts['rels']} relationships")
        return counts
    finally:
        await driver.close_driver()
        await db.close_pool()


def sync(full: bool = False, quiet: bool = False) -> dict:
    if full:
        graph_init.apply(reset=True, quiet=quiet)
    return asyncio.run(_run(full, quiet))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--full", action="store_true")
    sync(p.parse_args().full)
