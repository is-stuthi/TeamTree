"""Apply graph/0*.cypher (constraints, vector indexes) to Neo4j.

    python scripts/graph_init.py           # apply constraint + index scripts
    python scripts/graph_init.py --reset   # DETACH DELETE everything first
"""
import argparse
import sys
from pathlib import Path

from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.settings import ROOT, get_settings  # noqa: E402

GRAPH_DIR = ROOT / "graph"
SCRIPTS = ["001_constraints.cypher", "002_vector_indexes.cypher"]


def statements(text: str):
    buf = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        buf.append(line)
        if s.endswith(";"):
            yield "\n".join(buf).rstrip()[:-1]
            buf = []


def apply(reset: bool = False, quiet: bool = False) -> None:
    s = get_settings()
    with GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password)) as drv:
        drv.verify_connectivity()
        if reset:
            drv.execute_query("MATCH (n) DETACH DELETE n")
        for name in SCRIPTS:
            stmts = list(statements((GRAPH_DIR / name).read_text(encoding="utf-8")))
            for stmt in stmts:
                drv.execute_query(stmt)
            if not quiet:
                print(f"  {name:<28} {len(stmts):>3} statements")
        drv.execute_query("CALL db.awaitIndexes(60)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--reset", action="store_true")
    apply(p.parse_args().reset)
    print("Neo4j schema ready.")
