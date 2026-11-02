"""Deterministic capacity race test for decide_application.

The real procedure is called while a third connection holds the Project row lock,
so the CALL takes its snapshot (first SELECT) and then blocks. While it is blocked
we commit a member that fills the team, then release the lock. A capacity check
that reads from the stale snapshot would still see a free slot and overfill the
team; the fixed check (COUNT ... FOR SHARE) sees the committed member.
"""
import threading
import time

import pymysql

from app.settings import get_settings
from conftest import _connect, one


def _wait_for_lock_wait(conn, timeout=15.0) -> int:
    end = time.time() + timeout
    while time.time() < end:
        n = one(conn, "SELECT COUNT(*) n FROM performance_schema.data_lock_waits")["n"]
        if n:
            return n
        time.sleep(0.05)
    return 0


def test_accept_rechecks_capacity_against_committed_members(root_conn):
    s = get_settings()
    with root_conn.cursor() as cur:
        cur.execute("CALL create_project(5, 'Lock Race', NULL, NULL, 2, NULL, @p)")   # Dev owns; cap 2 incl. owner
        cur.execute("SELECT @p AS p")
        pid = cur.fetchone()["p"]
        cur.execute("INSERT INTO Application (applicant_id, p_id, msg) VALUES (6, %s, 'race')", (pid,))
        cur.execute("SELECT a_id FROM Application WHERE p_id = %s", (pid,))
        a_id = cur.fetchone()["a_id"]
        cur.execute("SELECT t_id FROM Team WHERE p_id = %s", (pid,))
        t_id = cur.fetchone()["t_id"]

    holder = _connect("root", s.mysql_root_password)
    holder.autocommit(False)
    with holder.cursor() as cur:
        cur.execute("SELECT * FROM Project WHERE p_id = %s FOR UPDATE", (pid,))

    result: dict[str, str] = {}
    app_conn = _connect("tt_app", s.tt_app_password)

    def accept():
        try:
            with app_conn.cursor() as cur:
                cur.execute("CALL decide_application(%s, 5, 'Accepted', NULL)", (a_id,))
            result["r"] = "ok"
        except pymysql.MySQLError as e:
            result["r"] = str(e.args[1])

    t = threading.Thread(target=accept)
    t.start()
    assert _wait_for_lock_wait(root_conn) >= 1, "CALL should be blocked on the Project lock"

    # A member joins (committed) while the accept is blocked: the team is now full (2/2).
    with root_conn.cursor() as cur:
        cur.execute("INSERT INTO Joins (t_id, u_id, role, join_date) VALUES (%s, 10, 'Member', CURDATE())", (t_id,))

    holder.commit()
    t.join(15)
    holder.close()
    app_conn.close()

    assert result.get("r") == "PROJECT_FULL", result
    assert one(root_conn, "SELECT fn_active_member_count(%s) n", (pid,))["n"] == 2
