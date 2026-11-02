"""P0: RBAC enforced by MySQL itself (rubric 12).

tt_app (role tt_member_app) can read and call procedures, but cannot write
Application/Joins/Skill directly or change protected columns. tt_report
(role tt_analyst) can read views only.
"""
from conftest import one, sql_error


def test_app_user_cannot_update_application_directly(app_conn):
    errno, _ = sql_error(app_conn, "UPDATE Application SET status='Accepted' WHERE a_id=1")
    assert errno == 1142


def test_app_user_cannot_insert_skill_or_membership(app_conn):
    assert sql_error(app_conn, "INSERT INTO Skill (s_name) VALUES ('Rust')")[0] == 1142
    assert sql_error(app_conn, "INSERT INTO Joins (t_id, u_id, join_date) VALUES (1, 6, CURDATE())")[0] == 1142


def test_column_level_privileges(app_conn):
    assert sql_error(app_conn, "UPDATE Users SET role='admin' WHERE id=3")[0] == 1143
    assert sql_error(app_conn, "UPDATE Project SET owner_id=3 WHERE p_id=1")[0] == 1143
    with app_conn.cursor() as cur:                       # an allowed column works
        assert cur.execute("UPDATE Users SET bio='updated' WHERE id=3") == 1


def test_create_project_procedure_builds_team_and_owner_membership(app_conn):
    with app_conn.cursor() as cur:
        cur.execute("CALL create_project(3, 'RBAC Demo', NULL, NULL, 4, NULL, @pid)")
        cur.execute("SELECT @pid AS pid")
        pid = cur.fetchone()["pid"]
    row = one(app_conn, "SELECT t.team_name, j.role FROM Team t JOIN Joins j ON j.t_id=t.t_id "
                        "WHERE t.p_id=%s AND j.u_id=3", (pid,))
    assert row == {"team_name": "RBAC Demo Team", "role": "Owner"}


def test_decide_application_requires_owner(app_conn):
    errno, msg = sql_error(app_conn, "CALL decide_application(1, 3, 'Accepted', NULL)")
    assert (errno, msg) == (1644, "NOT_OWNER")


def test_decide_application_accepts_atomically(app_conn):
    with app_conn.cursor() as cur:   # Alice (2) owns P1; Esha's application a_id=1 is pending
        cur.execute("CALL decide_application(1, 2, 'Accepted', 'ML Intern')")
    app = one(app_conn, "SELECT status, decision_date FROM Application WHERE a_id=1")
    member = one(app_conn, "SELECT role FROM TeamMemberDetails WHERE p_id=1 AND u_id=6 AND is_active")
    assert app["status"] == "Accepted" and app["decision_date"] is not None
    assert member == {"role": "ML Intern"}


def test_admin_only_procedures(app_conn):
    assert sql_error(app_conn, "CALL create_skill(2, 'Rust', 'Programming', @s)") == (1644, "NOT_ADMIN")
    with app_conn.cursor() as cur:
        cur.execute("CALL create_skill(1, 'Rust', 'Programming', @s)")
    assert one(app_conn, "SELECT COUNT(*) n FROM Skill WHERE s_name='Rust'")["n"] == 1


def test_report_user_reads_views_only(report_conn):
    assert sql_error(report_conn, "SELECT * FROM Users")[0] == 1142
    assert one(report_conn, "SELECT COUNT(*) n FROM TopInDemandSkills")["n"] >= 25
