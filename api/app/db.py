"""MySQL access. The API connects as the low-privilege `tt_app` user (role
tt_member_app), so guarded writes must go through stored procedures.

Transaction rule: procedures own their transactions (START TRANSACTION ... COMMIT
inside, with an EXIT HANDLER that rolls back). Never CALL a procedure inside a
client-side transaction: its START TRANSACTION would implicitly commit it.
Multi-statement writes that must be atomic belong in a procedure, not here."""
from contextlib import asynccontextmanager
from typing import Any

import aiomysql

from app.settings import get_settings

_pool: aiomysql.Pool | None = None
_report_pool: aiomysql.Pool | None = None     # tt_report (role tt_analyst): SELECT on views only


async def _create(user: str, password: str, maxsize: int) -> aiomysql.Pool:
    s = get_settings()
    return await aiomysql.create_pool(
        host=s.mysql_host, port=s.mysql_port, db=s.mysql_db, user=user, password=password,
        autocommit=True, minsize=1, maxsize=maxsize, charset="utf8mb4", cursorclass=aiomysql.DictCursor,
    )


async def init_pool() -> None:
    global _pool, _report_pool
    s = get_settings()
    _pool = await _create("tt_app", s.tt_app_password, 10)
    _report_pool = await _create("tt_report", s.tt_report_password, 4)


async def close_pool() -> None:
    global _pool, _report_pool
    for pool in (_pool, _report_pool):
        if pool is not None:
            pool.close()
            await pool.wait_closed()
    _pool = _report_pool = None


async def report_fetch_all(sql: str, params: Any = None) -> list[dict]:
    """Analytics reads as the read-only analyst user (views only, enforced by MySQL grants)."""
    if _report_pool is None:
        raise RuntimeError("report pool not initialised")
    async with _report_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return list(await cur.fetchall())


@asynccontextmanager
async def cursor():
    if _pool is None:
        raise RuntimeError("MySQL pool not initialised")
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            yield cur


async def fetch_all(sql: str, params: Any = None) -> list[dict]:
    async with cursor() as cur:
        await cur.execute(sql, params)
        return list(await cur.fetchall())


async def fetch_one(sql: str, params: Any = None) -> dict | None:
    async with cursor() as cur:
        await cur.execute(sql, params)
        return await cur.fetchone()


async def execute(sql: str, params: Any = None) -> int:
    """Run a DML statement; returns the affected row count."""
    async with cursor() as cur:
        return await cur.execute(sql, params)


async def execute_many(sql: str, rows: list[tuple]) -> int:
    async with cursor() as cur:
        return await cur.executemany(sql, rows)


async def call_proc(name: str, *args: Any, out: int = 0) -> list[Any]:
    """CALL a stored procedure with `out` trailing OUT parameters.
    Returns the OUT values in order (empty list when out=0)."""
    placeholders = ", ".join(["%s"] * len(args) + [f"@_o{i}" for i in range(out)])
    async with cursor() as cur:
        await cur.execute(f"CALL {name}({placeholders})", args)
        if not out:
            return []
        await cur.execute("SELECT " + ", ".join(f"@_o{i} AS o{i}" for i in range(out)))
        row = await cur.fetchone()
        return [row[f"o{i}"] for i in range(out)]


async def ping() -> bool:
    try:
        return (await fetch_one("SELECT 1 AS ok"))["ok"] == 1
    except Exception:
        return False
