"""Shared fixtures. Tests need `docker compose up -d db graph`.

fresh_db re-applies db/*.sql + seed once per test module (as root);
the API and `app_conn` connect as the restricted tt_app user.
"""
import sys
from pathlib import Path

import httpx
import pymysql
import pytest

API = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(API), str(API / "scripts")]

import graph_init  # noqa: E402
import migrate  # noqa: E402
from app.settings import get_settings  # noqa: E402


@pytest.fixture(scope="module")
def fresh_db():
    migrate.apply(quiet=True)


@pytest.fixture(scope="module")
def fresh_graph():
    graph_init.apply(reset=True, quiet=True)


@pytest.fixture(scope="module")
def synced_graph(fresh_db):
    """Fresh MySQL seed projected into a wiped Neo4j, plus graph-only seed data."""
    import sync_graph
    return sync_graph.sync(full=True, quiet=True)


def _connect(user: str, password: str) -> pymysql.Connection:
    s = get_settings()
    return pymysql.connect(host=s.mysql_host, port=s.mysql_port, user=user, password=password,
                           database=s.mysql_db, autocommit=True,
                           cursorclass=pymysql.cursors.DictCursor)


@pytest.fixture
def root_conn(fresh_db):
    conn = _connect("root", get_settings().mysql_root_password)
    yield conn
    conn.close()


@pytest.fixture
def app_conn(fresh_db):
    conn = _connect("tt_app", get_settings().tt_app_password)
    yield conn
    conn.close()


@pytest.fixture
def report_conn(fresh_db):
    conn = _connect("tt_report", get_settings().tt_report_password)
    yield conn
    conn.close()


@pytest.fixture
async def client(fresh_db):
    from app import db
    from app.graph import driver
    from app.main import app

    await db.init_pool()
    await driver.init_driver()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await driver.close_driver()
    await db.close_pool()


def sql_error(conn: pymysql.Connection, sql: str, params=None) -> tuple[int, str]:
    """Run SQL that must fail; return (errno, message)."""
    with pytest.raises(pymysql.MySQLError) as exc:
        with conn.cursor() as cur:
            cur.execute(sql, params)
    return exc.value.args[0], str(exc.value.args[1])


def one(conn: pymysql.Connection, sql: str, params=None) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()
