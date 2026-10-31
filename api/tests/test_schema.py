"""P0: constraints, generated-flag uniqueness, triggers, functions, views."""
from conftest import one, sql_error

USER_COLS = "(f_name, l_name, email, password_hash)"


def test_duplicate_email_rejected(root_conn):
    errno, msg = sql_error(root_conn, f"INSERT INTO Users {USER_COLS} VALUES ('A','B','alice@teamtree.dev','x')")
    assert errno == 1062 and "uq_users_email" in msg


def test_skill_name_unique_after_normalisation(root_conn):
    errno, msg = sql_error(root_conn, "INSERT INTO Skill (s_name) VALUES ('  python ')")
    assert errno == 1062 and "uq_skill_name_norm" in msg


def test_deadline_before_creation_violates_check(root_conn):
    errno, _ = sql_error(root_conn, "INSERT INTO Project (owner_id, p_name, deadline) "
                                    "VALUES (2, 'Past', CURDATE() - INTERVAL 1 DAY)")
    assert errno == 3819


def test_one_team_per_project(root_conn):
    errno, msg = sql_error(root_conn, "INSERT INTO Team (p_id, team_name) VALUES (1, 'Second team')")
    assert errno == 1062 and "uq_team_project" in msg


def test_joins_allows_history_but_one_active_row(root_conn):
    # Kavya (12) left team 4 in the seed, so rejoining is allowed (history kept) ...
    with root_conn.cursor() as cur:
        cur.execute("INSERT INTO Joins (t_id, u_id, role, join_date) VALUES (4, 12, 'Member', CURDATE())")
    assert one(root_conn, "SELECT COUNT(*) n FROM Joins WHERE t_id=4 AND u_id=12")["n"] == 2
    # ... but a second *active* row is not.
    errno, msg = sql_error(root_conn, "INSERT INTO Joins (t_id, u_id, role, join_date) VALUES (4, 12, 'Member', CURDATE())")
    assert errno == 1062 and "uq_joins_active" in msg


def test_only_one_pending_application_per_pair(root_conn):
    errno, msg = sql_error(root_conn, "INSERT INTO Application (applicant_id, p_id, msg) VALUES (9, 2, 'again')")
    assert errno == 1062 and "uq_application_pending" in msg


def test_trigger_blocks_self_application(root_conn):
    assert sql_error(root_conn, "INSERT INTO Application (applicant_id, p_id) VALUES (2, 1)") == (1644, "SELF_APPLICATION")


def test_trigger_blocks_full_project(root_conn):
    assert sql_error(root_conn, "INSERT INTO Application (applicant_id, p_id) VALUES (9, 5)") == (1644, "PROJECT_FULL")


def test_trigger_blocks_non_open_project(root_conn):
    assert sql_error(root_conn, "INSERT INTO Application (applicant_id, p_id) VALUES (6, 4)") == (1644, "PROJECT_NOT_OPEN")


def test_trigger_blocks_task_for_non_member(root_conn):
    assert sql_error(root_conn, "INSERT INTO Task (p_id, u_id, t_name) VALUES (3, 11, 'x')") == (1644, "ASSIGNEE_NOT_MEMBER")


def test_trigger_blocks_task_after_deadline(root_conn):
    errno, msg = sql_error(root_conn, "INSERT INTO Task (p_id, t_name, due_date) VALUES (3, 'late', CURDATE() + INTERVAL 1 YEAR)")
    assert (errno, msg) == (1644, "TASK_AFTER_DEADLINE")


def test_trigger_blocks_reopening_closed_project(root_conn):
    assert sql_error(root_conn, "UPDATE Project SET status='Open' WHERE p_id=7") == (1644, "PROJECT_REOPEN_FORBIDDEN")


def test_stored_functions(root_conn):
    row = one(root_conn, "SELECT fn_level_ord('Beginner') b, fn_level_ord('Expert') e, "
                         "fn_acceptance_rate(3) r3, fn_acceptance_rate(8) r8, "
                         "fn_active_member_count(5) m5, fn_is_admin(14) a14, fn_is_admin(2) a2")
    assert (row["b"], row["e"], row["m5"], row["a14"], row["a2"]) == (1, 4, 3, 1, 0)
    assert float(row["r3"]) == 0.5        # 1 accepted / 2 decided
    assert row["r8"] is None              # no decided applications


def test_skill_gap_view_reports_missing_docker(root_conn):
    row = one(root_conn, "SELECT qualified_members, shortfall FROM SkillGap WHERE p_id=3 AND s_name='Docker'")
    assert row == {"qualified_members": 0, "shortfall": 1}


def test_top_in_demand_skills_view(root_conn):
    row = one(root_conn, "SELECT projects_requiring, users_possessing FROM TopInDemandSkills WHERE s_name='React'")
    assert row["projects_requiring"] == 4 and row["users_possessing"] >= 5
