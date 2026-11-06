"""Smoke test for every stored function (db/002_functions.sql), called as tt_app
(EXECUTE grant) and cross-checked against the same answer written as plain SQL."""
import pytest
from conftest import one

LEVELS = [("Beginner", 1), ("Intermediate", 2), ("Advanced", 3), ("Expert", 4)]


def _val(conn, sql, params=None):
    return next(iter(one(conn, sql, params).values()))


@pytest.mark.parametrize("level,ordinal", LEVELS)
def test_fn_level_ord(app_conn, level, ordinal):
    assert _val(app_conn, "SELECT fn_level_ord(%s)", (level,)) == ordinal


def test_fn_level_ord_orders_the_enum(app_conn):
    assert _val(app_conn, "SELECT fn_level_ord('Expert') > fn_level_ord('Beginner')") == 1


def test_fn_active_member_count_matches_joins(app_conn):
    rows = app_conn.cursor()
    rows.execute("""SELECT p.p_id, fn_active_member_count(p.p_id) AS fn,
                           (SELECT COUNT(*) FROM Joins j JOIN Team t ON t.t_id = j.t_id
                             WHERE t.p_id = p.p_id AND j.leave_date IS NULL) AS hand
                      FROM Project p""")
    for r in rows.fetchall():
        assert r["fn"] == r["hand"], r


def test_fn_is_active_member(app_conn):
    owner = one(app_conn, "SELECT p_id, owner_id FROM Project ORDER BY p_id LIMIT 1")
    assert _val(app_conn, "SELECT fn_is_active_member(%s, %s)", (owner["p_id"], owner["owner_id"])) == 1
    outsider = _val(app_conn, """SELECT u.id FROM Users u WHERE NOT EXISTS (
                                   SELECT 1 FROM Joins j JOIN Team t ON t.t_id = j.t_id
                                    WHERE t.p_id = %s AND j.u_id = u.id AND j.leave_date IS NULL)
                                 LIMIT 1""", (owner["p_id"],))
    assert _val(app_conn, "SELECT fn_is_active_member(%s, %s)", (owner["p_id"], outsider)) == 0


def test_fn_acceptance_rate_ignores_pending_and_withdrawn(app_conn):
    cur = app_conn.cursor()
    cur.execute("""SELECT p_id, fn_acceptance_rate(p_id) AS fn,
                          SUM(status = 'Accepted') / NULLIF(SUM(status IN ('Accepted','Rejected')), 0) AS hand
                     FROM Application GROUP BY p_id""")
    rows = cur.fetchall()
    assert rows
    for r in rows:
        assert float(r["fn"] or 0) == pytest.approx(float(r["hand"] or 0), abs=1e-4), r


def test_fn_is_admin(app_conn):
    admin = _val(app_conn, "SELECT id FROM Users WHERE email = 'admin@teamtree.dev'")
    member = _val(app_conn, "SELECT id FROM Users WHERE email = 'alice@teamtree.dev'")
    assert _val(app_conn, "SELECT fn_is_admin(%s)", (admin,)) == 1
    assert _val(app_conn, "SELECT fn_is_admin(%s)", (member,)) == 0
