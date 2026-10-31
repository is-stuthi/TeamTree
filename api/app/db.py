"""MySQL access. The API connects as the low-privilege `tt_app` user (role
tt_member_app), so guarded writes must go through stored procedures."""
from contextlib import asynccontextmanager
from typing import Any

import aiomysql

from app.settings import get_settings

_pool: aiomysql.Pool | None = None


async def init_pool() -> None:
    global _pool
    s = get_settings()
    _pool = await aiomysql.create_pool(
        host=s.mysql_host, port=s.mysql_port, db=s.mysql_db,
        user="tt_app", password=s.tt_app_password,
        autocommit=True, minsize=1, maxsize=10, charset="utf8mb4",
        cursorclass=aiomysql.DictCursor,
    )


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


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
