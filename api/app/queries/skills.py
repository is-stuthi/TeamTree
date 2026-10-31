"""SQL for the skills router (public skill catalogue)."""

# JOIN + GROUP BY: catalogue with how many users hold each skill
LIST = """SELECT s.s_id, s.s_name, s.category, COUNT(h.u_id) AS users_possessing
            FROM Skill s LEFT JOIN user_has_skill h ON h.s_id = s.s_id
           WHERE (%(q)s IS NULL OR s.s_name LIKE CONCAT('%%', %(q)s, '%%'))
             AND (%(category)s IS NULL OR s.category = %(category)s)
           GROUP BY s.s_id, s.s_name, s.category
           ORDER BY s.category, s.s_name"""

ONE = """SELECT s.s_id, s.s_name, s.category, COUNT(h.u_id) AS users_possessing
           FROM Skill s LEFT JOIN user_has_skill h ON h.s_id = s.s_id
          WHERE s.s_id = %s GROUP BY s.s_id, s.s_name, s.category"""

CATEGORIES = "SELECT DISTINCT category FROM Skill WHERE category IS NOT NULL ORDER BY category"
