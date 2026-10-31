"""SQL for the users router. DML rows are labelled for the rubric (see db/queries/dml_demo.sql)."""

ME = """SELECT id, f_name, m_name, l_name, email, role, bio, location, dob,
               experience_level, availability, created_at
          FROM Users WHERE id = %s"""

PUBLIC = """SELECT id, CONCAT(f_name, ' ', l_name) AS name, bio, location, experience_level, availability
              FROM Users WHERE id = %s AND is_active"""

SKILLS = """SELECT s.s_id, s.s_name, s.category, h.u_s_level
              FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id
             WHERE h.u_id = %s ORDER BY s.category, s.s_name"""

# Columns tt_app may UPDATE (column-level GRANT in db/007_rbac.sql)
PROFILE_COLUMNS = ("f_name", "m_name", "l_name", "bio", "location", "dob", "experience_level", "availability")

# D1 [MULTI-ROW INSERT + UPSERT] add several skills at once
BULK_UPSERT_SKILLS = ("INSERT INTO user_has_skill (u_id, s_id, u_s_level) VALUES {rows} AS new "
                      "ON DUPLICATE KEY UPDATE u_s_level = new.u_s_level")

# D6 [UPSERT] set one skill's proficiency
UPSERT_SKILL = ("INSERT INTO user_has_skill (u_id, s_id, u_s_level) VALUES (%s, %s, %s) AS new "
                "ON DUPLICATE KEY UPDATE u_s_level = new.u_s_level")

# D5 [DELETE] remove a skill from a profile
DELETE_SKILL = "DELETE FROM user_has_skill WHERE u_id = %s AND s_id = %s"

PASSWORD_HASH = "SELECT password_hash FROM Users WHERE id = %s"
SET_PASSWORD = "UPDATE Users SET password_hash = %s WHERE id = %s"


def profile_update(fields: list[str]) -> str:
    cols = [f for f in fields if f in PROFILE_COLUMNS]
    return "UPDATE Users SET " + ", ".join(f"{c} = %s" for c in cols) + " WHERE id = %s"
