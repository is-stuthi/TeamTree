"""Smoke test for every catalogue query (Q1-Q14 + browse/applicants) and DML demo
(D1-D7), run straight from db/queries/*.sql so the viva files can't rot.

Queries run as tt_app (the API's user); Q10 also as tt_report (views only).
The DML demos run as root, in file order, on one fresh seed: they modify data."""
import pytest
from catalogue import blocks, run_block
from conftest import one

Q = blocks("catalogue.sql")
D = blocks("dml_demo.sql")

# Minimum row counts the seed guarantees (0 = must run, may legitimately be empty).
MIN_ROWS = {"Q1": 1, "Q2": 1, "Q3": 1, "Q4": 0, "Q5": 0, "Q6": 1, "Q7": 10, "Q8": 3,
            "Q9": 30, "Q10": 3, "Q11": 1, "Q12": 1, "Q13": 12, "Q14": 0, "Q-browse": 0, "Q-applicants": 1}


def test_catalogue_is_complete():
    assert {f"Q{i}" for i in range(1, 15)} <= Q.keys()
    assert {f"D{i}" for i in range(1, 8)} == D.keys()
    assert set(MIN_ROWS) == set(Q)


@pytest.mark.parametrize("label", list(Q))
def test_query_runs_as_app_user(app_conn, label):
    rows = run_block(app_conn, Q[label])
    assert len(rows) >= MIN_ROWS[label], f"{label} returned {len(rows)} rows"


def test_q1_is_one_project_row(app_conn):
    (row,) = run_block(app_conn, Q["Q1"])
    assert row["p_id"] == 3 and row["team_size"] >= 1 and row["owner_name"]


def test_q8_tree_is_three_levels_deep(app_conn):
    rows = run_block(app_conn, Q["Q8"])
    assert max(r["depth"] for r in rows) == 2
    assert all(r["path"].count(" › ") == r["depth"] for r in rows)


def test_q9_is_a_gapless_30_day_series(app_conn):
    rows = run_block(app_conn, Q["Q9"])
    assert len(rows) == 30
    days = [r["day"] for r in rows]
    assert all((b - a).days == 1 for a, b in zip(days, days[1:]))


def test_q10_runs_as_analyst_on_views(report_conn):
    rows = run_block(report_conn, Q["Q10"])
    assert rows and all(r["rank_in_category"] <= 3 for r in rows)


def test_q11_pairs_are_ordered_and_unique(app_conn):
    rows = run_block(app_conn, Q["Q11"])
    pairs = [(r["u1"], r["u2"]) for r in rows]
    assert all(a < b for a, b in pairs) and len(pairs) == len(set(pairs))


# ---------------- DML demos (root, file order, cumulative) ----------------

def _skill(conn, uid, sid):
    row = one(conn, "SELECT u_s_level FROM user_has_skill WHERE u_id=%s AND s_id=%s", (uid, sid))
    return row and row["u_s_level"]


def test_d1_multi_row_upsert(root_conn):
    run_block(root_conn, D["D1"])
    assert _skill(root_conn, 6, 11) == "Beginner" and _skill(root_conn, 6, 1) == "Intermediate"


def test_d2_insert_select_copies_requirements(root_conn):
    run_block(root_conn, D["D2"])
    missing = one(root_conn, """SELECT COUNT(*) n FROM Requires s WHERE s.p_id = 1 AND NOT EXISTS
                                (SELECT 1 FROM Requires t WHERE t.p_id = 8 AND t.s_id = s.s_id
                                    AND t.req_role = s.req_role)""")
    assert missing["n"] == 0


def test_d3_update_join_blocks_open_tasks(root_conn):
    run_block(root_conn, D["D3"])
    assert one(root_conn, "SELECT status FROM Project WHERE p_id = 3")["status"] == "Closed"
    left = one(root_conn, "SELECT COUNT(*) n FROM Task WHERE p_id = 3 AND status IN ('To Do','In Progress')")
    assert left["n"] == 0


def test_d4_soft_delete_keeps_the_row(root_conn):
    (row,) = run_block(root_conn, D["D4"])
    assert row["id"] == 12 and not row["is_active"]


def test_d5_delete_skill(root_conn):
    run_block(root_conn, D["D5"])
    assert _skill(root_conn, 6, 11) is None


def test_d6_upsert_one_level(root_conn):
    run_block(root_conn, D["D6"])
    assert _skill(root_conn, 6, 16) == "Advanced"


def test_d7_accept_is_atomic(root_conn):
    (row,) = run_block(root_conn, D["D7"])
    assert row["status"] == "Accepted" and row["decision_date"] and row["role"] == "Data Labeller"
