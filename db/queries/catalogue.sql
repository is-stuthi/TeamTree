-- =========================================================
-- Query catalogue (rubric 7). NOT part of the migration.
-- Each query: -- Qn [TYPE] question  ·  used by: <endpoint>
-- TYPE in: JOIN, NESTED, CORRELATED, RECURSIVE CTE, CTE+WINDOW, SELF-JOIN, UNION
-- Parameters are user variables (SET @pid = ...) so every query runs as-is in a
-- MySQL client; the API binds the same values as query parameters.
-- Phases append here as each query is wired to an endpoint (see phases/README.md).
-- =========================================================
USE teamtree;

-- ---------------------------------------------------------
-- Q1 [JOIN, 5 tables] Project detail: owner, team, active member count, domains
-- used by: GET /projects/{p_id}   (api/app/queries/projects.py DETAIL)
-- ---------------------------------------------------------
SET @pid = 3;
SELECT p.p_id, p.p_name, p.description, p.deadline, p.status, p.max_team_size,
       p.creation_date, p.owner_id, CONCAT(u.f_name, ' ', u.l_name) AS owner_name,
       u.bio AS owner_bio, t.team_name, COUNT(DISTINCT j.j_id) AS team_size,
       GROUP_CONCAT(DISTINCT d.d_name ORDER BY d.d_name SEPARATOR ',') AS domains,
       (p.deadline IS NOT NULL AND p.deadline < CURDATE() AND p.status IN ('Open','Ongoing')) AS is_overdue
  FROM Project p
  JOIN Users u       ON u.id = p.owner_id
  JOIN Team t        ON t.p_id = p.p_id
  LEFT JOIN Joins j  ON j.t_id = t.t_id AND j.leave_date IS NULL
  LEFT JOIN Domain d ON d.project_id = p.p_id
 WHERE p.p_id = @pid
 GROUP BY p.p_id, u.id, t.t_id;

-- ---------------------------------------------------------
-- Q6 [CORRELATED EXISTS + correlated scalar subqueries]
-- Open projects where the user meets at least one requirement at the required level
-- used by: GET /users/me/recommended-projects   (api/app/queries/discovery.py RECOMMENDED)
-- ---------------------------------------------------------
SET @uid = 11;
SELECT pl.p_id, pl.p_name,
       (SELECT COUNT(*) FROM Requires r
          JOIN user_has_skill h ON h.s_id = r.s_id AND h.u_id = @uid
         WHERE r.p_id = pl.p_id
           AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)) AS matched_requirements,
       (SELECT COUNT(*) FROM Requires r WHERE r.p_id = pl.p_id) AS total_requirements
  FROM OpenProjects pl
 WHERE pl.owner_id <> @uid
   AND NOT fn_is_active_member(pl.p_id, @uid)
   AND EXISTS (SELECT 1 FROM Requires r
                 JOIN user_has_skill h ON h.s_id = r.s_id
                WHERE r.p_id = pl.p_id AND h.u_id = @uid
                  AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level))
 ORDER BY matched_requirements DESC, pl.deadline;

-- ---------------------------------------------------------
-- Q-browse [NESTED IN + EXISTS] Browse filter: projects requiring a skill in a domain
-- used by: GET /projects?skill=&domain=   (api/app/queries/projects.py LISTING)
-- ---------------------------------------------------------
SET @skill = 16, @domain = 'Security';
SELECT pl.p_id, pl.p_name, pl.status, pl.domains
  FROM ProjectListing pl
 WHERE pl.p_id IN (SELECT r.p_id FROM Requires r WHERE r.s_id = @skill)
   AND EXISTS (SELECT 1 FROM Domain d WHERE d.project_id = pl.p_id AND d.d_name = @domain);

-- ---------------------------------------------------------
-- Q-applicants [CORRELATED subqueries in SELECT] Each applicant's skills and
-- how many of the project's requirements they meet
-- used by: GET /projects/{p_id}/applications   (api/app/queries/applications.py RECEIVED)
-- ---------------------------------------------------------
SET @pid = 1;
SELECT a.a_id, CONCAT(u.f_name, ' ', u.l_name) AS applicant, a.status,
       (SELECT GROUP_CONCAT(CONCAT(s.s_name, ' (', h.u_s_level, ')') SEPARATOR ', ')
          FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id
         WHERE h.u_id = a.applicant_id) AS skills,
       (SELECT COUNT(*) FROM Requires r
          JOIN user_has_skill h ON h.s_id = r.s_id AND h.u_id = a.applicant_id
         WHERE r.p_id = a.p_id
           AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)) AS matched_requirements
  FROM Application a JOIN Users u ON u.id = a.applicant_id
 WHERE a.p_id = @pid
 ORDER BY a.status = 'Pending' DESC, a.a_date DESC;
