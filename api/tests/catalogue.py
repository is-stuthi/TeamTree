"""Split db/queries/*.sql into labelled blocks (Q1, Q-browse, D3, ...) so the smoke
tests run exactly the SQL shown in the viva, not a copy of it."""
import re

from app.settings import ROOT
from migrate import statements

QUERIES = ROOT / "db" / "queries"
_HEADER = re.compile(r"^-- ([QD][\w-]+) \[", re.MULTILINE)


def blocks(name: str) -> dict[str, list[str]]:
    """{label: [statement, ...]} in file order; the file's leading USE is dropped."""
    text = (QUERIES / name).read_text(encoding="utf-8")
    marks = list(_HEADER.finditer(text))
    out: dict[str, list[str]] = {}
    for m, nxt in zip(marks, marks[1:] + [None]):
        body = text[m.start(): nxt.start() if nxt else len(text)]
        out[m.group(1)] = [s for s in statements(body) if not s.upper().startswith("USE ")]
    return out


def run_block(conn, stmts: list[str]) -> list[dict]:
    """Run every statement of a block; return the rows of the last one that produced any."""
    rows: list[dict] = []
    with conn.cursor() as cur:
        for stmt in stmts:
            cur.execute(stmt)
            if cur.description:
                rows = list(cur.fetchall())
    return rows
