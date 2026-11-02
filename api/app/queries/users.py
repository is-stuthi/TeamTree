"""SQL for the users router. DML rows are labelled for the rubric (see db/queries/dml_demo.sql)."""

ME = """SELECT id, f_name, m_name, l_name, email, role, bio, location, dob,
               experience_level, availability, created_at
          FROM Users WHERE id = %s"""

# Q7 [CORRELATED scalar subquery in SELECT] each user's strongest skill
PUBLIC = """SELECT u.id, CONCAT(u.f_name, ' ', u.l_name) AS name, u.bio, u.location,
       u.experience_level, u.availability,
       (SELECT s.s_name FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id
         WHERE h.u_id = u.id
         ORDER BY fn_level_ord(h.u_s_level) DESC, s.s_name LIMIT 1) AS strongest_skill
  FROM Users u WHERE u.id = %s AND u.is_active"""

SKILLS = """SELECT s.s_id, s.s_name, s.category, h.u_s_level
              FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id
             WHERE h.u_id = %s ORDER BY s.category, s.s_name"""

# Columns tt_app may UPDATE (column-level GRANT in db/007_rbac.sql)
PROFILE_COLUMNS = ("f_name", "m_name", "l_name", "bio", "location", "dob", "experience_level", "availability")
NOT_NULL_COLUMNS = {"f_name", "l_name", "experience_level", "availability"}

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
