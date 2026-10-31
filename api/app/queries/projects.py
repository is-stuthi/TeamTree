"""SQL for the projects router. Rubric-labelled queries are mirrored in db/queries/*.sql."""

LISTING = """SELECT * FROM ProjectListing pl
 WHERE (%(status)s IS NULL OR pl.status = %(status)s)
   AND (%(q)s IS NULL OR pl.p_name LIKE CONCAT('%%', %(q)s, '%%')
                      OR pl.description LIKE CONCAT('%%', %(q)s, '%%'))
   AND (%(domain)s IS NULL OR EXISTS (SELECT 1 FROM Domain d
                                       WHERE d.project_id = pl.p_id AND d.d_name = %(domain)s))
   AND (%(skill)s IS NULL OR pl.p_id IN (SELECT r.p_id FROM Requires r WHERE r.s_id = %(skill)s))
   AND (%(deadline_before)s IS NULL OR pl.deadline <= %(deadline_before)s)
 ORDER BY pl.status = 'Open' DESC, pl.deadline IS NULL, pl.deadline, pl.p_id"""

# Q1 [JOIN, 5 tables] project detail: owner, team, active members, domains
DETAIL = """SELECT p.p_id, p.p_name, p.description, p.deadline, p.status, p.max_team_size,
       p.creation_date, p.owner_id, CONCAT(u.f_name, ' ', u.l_name) AS owner_name,
       u.bio AS owner_bio, t.team_name, COUNT(DISTINCT j.j_id) AS team_size,
       GROUP_CONCAT(DISTINCT d.d_name ORDER BY d.d_name SEPARATOR ',') AS domains,
       (p.deadline IS NOT NULL AND p.deadline < CURDATE() AND p.status IN ('Open','Ongoing')) AS is_overdue
  FROM Project p
  JOIN Users u      ON u.id = p.owner_id
  JOIN Team t       ON t.p_id = p.p_id
  LEFT JOIN Joins j ON j.t_id = t.t_id AND j.leave_date IS NULL
  LEFT JOIN Domain d ON d.project_id = p.p_id
 WHERE p.p_id = %s
 GROUP BY p.p_id, u.id, t.t_id"""

REQUIREMENTS = """SELECT s_id, s_name, category, req_role, p_s_level, req_count
                    FROM ProjectSkillRequirements WHERE p_id = %s
                   ORDER BY level_ord DESC, s_name"""

VIEWER = """SELECT fn_is_active_member(%(p)s, %(u)s) AS is_member,
       (SELECT a_id FROM Application WHERE p_id = %(p)s AND applicant_id = %(u)s
                                       AND status = 'Pending') AS pending_application_id"""

OWNER = "SELECT owner_id FROM Project WHERE p_id = %s"

INSERT_DOMAINS = "INSERT INTO Domain (project_id, d_name) VALUES (%s, %s)"
DELETE_DOMAINS = "DELETE FROM Domain WHERE project_id = %s"

# Columns tt_app may UPDATE on Project (column-level GRANT in db/007_rbac.sql)
PATCH_COLUMNS = ("p_name", "description", "deadline", "status", "max_team_size")

# D3 [UPDATE ... JOIN] closing a project blocks its unfinished tasks
BLOCK_TASKS_ON_CLOSE = """UPDATE Task t JOIN Project p ON p.p_id = t.p_id
   SET t.status = 'Blocked'
 WHERE p.p_id = %s AND p.status = 'Closed' AND t.status IN ('To Do', 'In Progress')"""


def patch(fields: list[str]) -> str:
    cols = [f for f in fields if f in PATCH_COLUMNS]
    return "UPDATE Project SET " + ", ".join(f"{c} = %s" for c in cols) + " WHERE p_id = %s"


def split_csv(row: dict, *keys: str) -> dict:
    """GROUP_CONCAT columns -> lists."""
    return {**row, **{k: (row.get(k) or "").split(",") if row.get(k) else [] for k in keys}}
