"""SQL for "my projects" and recommendations."""

MY_PROJECTS = """SELECT pl.*, tm.role AS my_role, (pl.owner_id = %(u)s) AS is_owner
                   FROM TeamMemberDetails tm
                   JOIN ProjectListing pl ON pl.p_id = tm.p_id
                  WHERE tm.u_id = %(u)s AND tm.is_active
                  ORDER BY is_owner DESC, pl.status = 'Open' DESC, pl.deadline IS NULL, pl.deadline"""

# Q6 [CORRELATED EXISTS] Open projects where the user meets at least one requirement
RECOMMENDED = """SELECT pl.*,
       (SELECT COUNT(*) FROM Requires r
          JOIN user_has_skill h ON h.s_id = r.s_id AND h.u_id = %(u)s
         WHERE r.p_id = pl.p_id
           AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)) AS matched_requirements,
       (SELECT COUNT(*) FROM Requires r WHERE r.p_id = pl.p_id) AS total_requirements
  FROM OpenProjects pl
 WHERE pl.owner_id <> %(u)s
   AND NOT fn_is_active_member(pl.p_id, %(u)s)
   AND EXISTS (SELECT 1 FROM Requires r
                 JOIN user_has_skill h ON h.s_id = r.s_id
                WHERE r.p_id = pl.p_id AND h.u_id = %(u)s
                  AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level))
 ORDER BY matched_requirements DESC, pl.deadline IS NULL, pl.deadline
 LIMIT %(limit)s"""
