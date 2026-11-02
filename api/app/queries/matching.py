"""SQL for candidate matching and the skill-gap report."""

REQUIREMENTS = """SELECT r.s_id, s.s_name, fn_level_ord(r.p_s_level) AS level
                    FROM Requires r JOIN Skill s ON s.s_id = r.s_id WHERE r.p_id = %s"""

# Candidates exclude: the owner, active members, users with a pending application, inactive users.
_ELIGIBLE = """u.is_active
   AND u.id <> (SELECT owner_id FROM Project WHERE p_id = %(p)s)
   AND NOT fn_is_active_member(%(p)s, u.id)
   AND NOT EXISTS (SELECT 1 FROM Application a
                    WHERE a.p_id = %(p)s AND a.applicant_id = u.id AND a.status = 'Pending')"""

# Q3 [NESTED IN] users having ANY skill the project requires
ANY_SKILL = f"""SELECT u.id FROM Users u
 WHERE u.id IN (SELECT h.u_id FROM user_has_skill h
                 WHERE h.s_id IN (SELECT r.s_id FROM Requires r WHERE r.p_id = %(p)s))
   AND {_ELIGIBLE}"""

# Q4 [NESTED NOT EXISTS: relational division] users meeting EVERY requirement at its level
ALL_SKILLS = f"""SELECT u.id FROM Users u
 WHERE NOT EXISTS (
         SELECT 1 FROM Requires r WHERE r.p_id = %(p)s
            AND NOT EXISTS (SELECT 1 FROM user_has_skill h
                             WHERE h.u_id = u.id AND h.s_id = r.s_id
                               AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)))
   AND {_ELIGIBLE}"""

PROFILES = """SELECT id AS u_id, CONCAT(f_name, ' ', l_name) AS name, experience_level, availability
                FROM Users WHERE id IN ({ids})"""

SKILLS = """SELECT u_id, s_id, fn_level_ord(u_s_level) AS level FROM user_has_skill
             WHERE u_id IN ({ids}) AND s_id IN (SELECT s_id FROM Requires WHERE p_id = %s)"""

# Has been on a team (ever) of another project sharing a domain with this one
DOMAIN_MATCH = """SELECT DISTINCT j.u_id FROM Joins j
  JOIN Team t   ON t.t_id = j.t_id
  JOIN Domain d ON d.project_id = t.p_id
 WHERE j.u_id IN ({ids}) AND t.p_id <> %s
   AND d.d_name IN (SELECT d_name FROM Domain WHERE project_id = %s)"""

SKILL_GAP = """SELECT s_id, s_name, req_role, required_level, req_count,
                      members_with_skill, qualified_members, shortfall
                 FROM SkillGap WHERE p_id = %s ORDER BY shortfall DESC, s_name"""


def placeholders(n: int) -> str:
    return ", ".join(["%s"] * n)
