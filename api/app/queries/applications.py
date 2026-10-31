"""SQL for applications. Writes go through procedures (apply_to_project,
decide_application, withdraw_application); tt_app cannot write Application directly."""

_BASE = """SELECT a.a_id, a.p_id, p.p_name, p.status AS project_status, a.applicant_id,
       CONCAT(u.f_name, ' ', u.l_name) AS applicant_name, a.msg, a.status, a.a_date, a.decision_date
  FROM Application a
  JOIN Project p ON p.p_id = a.p_id
  JOIN Users u   ON u.id = a.applicant_id"""

ONE = _BASE + " WHERE a.a_id = %s"

MINE = _BASE + " WHERE a.applicant_id = %s ORDER BY a.status = 'Pending' DESC, a.a_date DESC"

# Correlated subqueries: each applicant's skills and how many requirements they meet
RECEIVED = """SELECT a.a_id, a.p_id, p.p_name, p.status AS project_status, a.applicant_id,
       CONCAT(u.f_name, ' ', u.l_name) AS applicant_name, a.msg, a.status, a.a_date, a.decision_date,
       u.experience_level, u.availability,
       (SELECT GROUP_CONCAT(CONCAT(s.s_name, '|', h.u_s_level)
                            ORDER BY fn_level_ord(h.u_s_level) DESC, s.s_name SEPARATOR ';')
          FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id
         WHERE h.u_id = a.applicant_id) AS skills,
       (SELECT COUNT(*) FROM Requires r
          JOIN user_has_skill h ON h.s_id = r.s_id AND h.u_id = a.applicant_id
         WHERE r.p_id = a.p_id
           AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)) AS matched_requirements,
       (SELECT COUNT(*) FROM Requires r WHERE r.p_id = a.p_id) AS total_requirements
  FROM Application a
  JOIN Project p ON p.p_id = a.p_id
  JOIN Users u   ON u.id = a.applicant_id
 WHERE a.p_id = %(p)s AND (%(status)s IS NULL OR a.status = %(status)s)
 ORDER BY a.status = 'Pending' DESC, a.a_date DESC"""


def parse_skills(row: dict) -> dict:
    pairs = [s.split("|", 1) for s in (row.get("skills") or "").split(";") if "|" in s]
    return {**row, "skills": [{"s_name": n, "level": lvl} for n, lvl in pairs]}
