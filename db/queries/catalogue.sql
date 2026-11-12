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

-- ---------------------------------------------------------
-- Q5 [CORRELATED subquery in HAVING] Active members who completed more tasks
-- than their team's average (done tasks / active members)
-- used by: GET /projects/{p_id}/team/top-contributors   (api/app/queries/teams.py)
-- ---------------------------------------------------------
SET @pid = 4;
SELECT j.u_id, CONCAT(u.f_name, ' ', u.l_name) AS member_name, COUNT(tk.task_id) AS done
  FROM Joins j
  JOIN Team t  ON t.t_id = j.t_id
  JOIN Users u ON u.id = j.u_id
  JOIN Task tk ON tk.p_id = t.p_id AND tk.u_id = j.u_id AND tk.status = 'Done'
 WHERE t.p_id = @pid AND j.leave_date IS NULL
 GROUP BY t.t_id, t.p_id, j.u_id, u.f_name, u.l_name
HAVING COUNT(tk.task_id) > (
       SELECT COUNT(*) / NULLIF((SELECT COUNT(*) FROM Joins j2
                                  WHERE j2.t_id = t.t_id AND j2.leave_date IS NULL), 0)
         FROM Task t2
         JOIN Joins j3 ON j3.t_id = t.t_id AND j3.u_id = t2.u_id AND j3.leave_date IS NULL
        WHERE t2.p_id = t.p_id AND t2.status = 'Done')
 ORDER BY done DESC;

-- ---------------------------------------------------------
-- Q8 [RECURSIVE CTE] Subtask tree with depth and breadcrumb path (depth-first order)
-- used by: GET /projects/{p_id}/tasks/tree   (api/app/queries/tasks.py TREE)
-- ---------------------------------------------------------
SET @pid = 4;
WITH RECURSIVE tree AS (
    SELECT task_id, 0 AS depth, CAST(t_name AS CHAR(1000)) AS path,
           CAST(LPAD(task_id, 8, '0') AS CHAR(1000)) AS sort_key
      FROM Task WHERE p_id = @pid AND parent_task_id IS NULL
    UNION ALL
    SELECT c.task_id, tree.depth + 1, CONCAT(tree.path, ' › ', c.t_name),
           CONCAT(tree.sort_key, '/', LPAD(c.task_id, 8, '0'))
      FROM Task c JOIN tree ON c.parent_task_id = tree.task_id
)
SELECT tree.depth, CONCAT(REPEAT('    ', tree.depth), tk.t_name) AS task, tk.status, tree.path
  FROM tree JOIN Task tk ON tk.task_id = tree.task_id
 ORDER BY tree.sort_key;

-- ---------------------------------------------------------
-- Q3 [NESTED IN, two levels] Candidates having ANY skill the project requires
-- (excluding owner, active members, pending applicants, inactive users)
-- used by: GET /projects/{p_id}/candidates   (api/app/queries/matching.py ANY_SKILL)
-- ---------------------------------------------------------
SET @pid = 3;
SELECT u.id, CONCAT(u.f_name, ' ', u.l_name) AS name
  FROM Users u
 WHERE u.id IN (SELECT h.u_id FROM user_has_skill h
                 WHERE h.s_id IN (SELECT r.s_id FROM Requires r WHERE r.p_id = @pid))
   AND u.is_active
   AND u.id <> (SELECT owner_id FROM Project WHERE p_id = @pid)
   AND NOT fn_is_active_member(@pid, u.id);

-- ---------------------------------------------------------
-- Q4 [NESTED NOT EXISTS: relational division] Users who meet EVERY requirement
-- of the project at (or above) the required level
-- used by: GET /projects/{p_id}/candidates?full=1   (api/app/queries/matching.py ALL_SKILLS)
-- ---------------------------------------------------------
SET @pid = 3;
SELECT u.id, CONCAT(u.f_name, ' ', u.l_name) AS name
  FROM Users u
 WHERE NOT EXISTS (
         SELECT 1 FROM Requires r WHERE r.p_id = @pid
            AND NOT EXISTS (SELECT 1 FROM user_has_skill h
                             WHERE h.u_id = u.id AND h.s_id = r.s_id
                               AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)))
   AND u.is_active
   AND u.id <> (SELECT owner_id FROM Project WHERE p_id = @pid)
   AND NOT fn_is_active_member(@pid, u.id);

-- ---------------------------------------------------------
-- Q7 [CORRELATED scalar subquery in SELECT] Each active user's strongest skill
-- used by: GET /users/{user_id}   (api/app/queries/users.py PUBLIC)
-- ---------------------------------------------------------
SELECT u.id, CONCAT(u.f_name, ' ', u.l_name) AS name,
       (SELECT s.s_name FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id
         WHERE h.u_id = u.id
         ORDER BY fn_level_ord(h.u_s_level) DESC, s.s_name LIMIT 1) AS strongest_skill
  FROM Users u WHERE u.is_active ORDER BY u.id;

-- ---------------------------------------------------------
-- Q2 [LEFT JOIN + GROUP BY + HAVING] Projects that have received no applications
-- used by: GET /analytics/projects   (api/app/queries/analytics.py BASE_NO_APPLICATIONS)
-- ---------------------------------------------------------
SELECT p.p_id, p.p_name, p.status, COUNT(a.a_id) AS applications
  FROM Project p LEFT JOIN Application a ON a.p_id = p.p_id
 GROUP BY p.p_id, p.p_name, p.status
HAVING COUNT(a.a_id) = 0;

-- ---------------------------------------------------------
-- Q9 [RECURSIVE CTE: date series] Applications per day, last 30 days, gaps filled with 0
-- used by: GET /analytics/applications -> timeline   (BASE_TIMELINE)
-- ---------------------------------------------------------
WITH RECURSIVE days AS (
    SELECT CURDATE() - INTERVAL 29 DAY AS d
    UNION ALL SELECT d + INTERVAL 1 DAY FROM days WHERE d < CURDATE())
SELECT days.d AS day, COUNT(a.a_id) AS applications
  FROM days LEFT JOIN Application a ON DATE(a.a_date) = days.d
 GROUP BY days.d ORDER BY days.d;

-- ---------------------------------------------------------
-- Q10 [CTE + WINDOW: ROW_NUMBER OVER PARTITION] Top 3 in-demand skills per category
-- (runs on the TopInDemandSkills view, itself a CTE + RANK() view, as the read-only analyst)
-- used by: GET /analytics/skills -> top_by_category   (VIEW_TOP_BY_CATEGORY)
-- ---------------------------------------------------------
WITH ranked AS (
    SELECT category, s_name, projects_requiring,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY projects_requiring DESC, s_name) AS rn
      FROM TopInDemandSkills WHERE projects_requiring > 0)
SELECT category, s_name, projects_requiring, rn AS rank_in_category
  FROM ranked WHERE rn <= 3 ORDER BY category, rn;

-- ---------------------------------------------------------
-- Q11 [SELF-JOIN] Pairs of users who have shared a team (history included)
-- used by: MySQL -> Neo4j sync, builds COLLABORATED_WITH edges   (api/app/graph/source.py PAIRS)
-- ---------------------------------------------------------
SELECT LEAST(a.u_id, b.u_id) AS u1, GREATEST(a.u_id, b.u_id) AS u2, COUNT(DISTINCT a.t_id) AS shared_teams
  FROM Joins a JOIN Joins b ON a.t_id = b.t_id AND a.u_id < b.u_id
 GROUP BY u1, u2 ORDER BY shared_teams DESC, u1, u2;

-- ---------------------------------------------------------
-- Q12 [UNION ALL] A user's activity feed: applications, joins, leaves, tasks
-- used by: GET /users/me/activity   (BASE_ACTIVITY_FEED)
-- ---------------------------------------------------------
SET @uid = 7;
SELECT * FROM (
    SELECT a.a_date AS at, 'application' AS kind, CONCAT('Applied to ', p.p_name, ' (', a.status, ')') AS what
      FROM Application a JOIN Project p ON p.p_id = a.p_id WHERE a.applicant_id = @uid
    UNION ALL
    SELECT j.join_date, 'team', CONCAT('Joined ', t.team_name, ' as ', j.role)
      FROM Joins j JOIN Team t ON t.t_id = j.t_id WHERE j.u_id = @uid
    UNION ALL
    SELECT j.leave_date, 'team', CONCAT('Left ', t.team_name)
      FROM Joins j JOIN Team t ON t.t_id = j.t_id WHERE j.u_id = @uid AND j.leave_date IS NOT NULL
    UNION ALL
    SELECT tk.created_at, 'task', CONCAT('Task: ', tk.t_name, ' (', tk.status, ')')
      FROM Task tk WHERE tk.u_id = @uid
) feed ORDER BY at DESC;

-- ---------------------------------------------------------
-- Q13 [RECURSIVE CTE: week series + UNION ALL] A user's activity per week, last 12 weeks, gaps filled with 0
-- used by: GET /users/me/insights → weekly_activity   (BASE_ACTIVITY_WEEKLY), dashboard line chart
-- ---------------------------------------------------------
SET @uid = 7;
WITH RECURSIVE weeks AS (
    SELECT CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY - INTERVAL 11 WEEK AS w
    UNION ALL SELECT w + INTERVAL 1 WEEK FROM weeks
     WHERE w < CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY)
SELECT CAST(weeks.w AS CHAR) AS week, COUNT(feed.at) AS activity
  FROM weeks LEFT JOIN (
    SELECT a.a_date AS at FROM Application a WHERE a.applicant_id = @uid
    UNION ALL SELECT j.join_date FROM Joins j WHERE j.u_id = @uid
    UNION ALL SELECT j.leave_date FROM Joins j WHERE j.u_id = @uid AND j.leave_date IS NOT NULL
    UNION ALL SELECT tk.created_at FROM Task tk WHERE tk.u_id = @uid
  ) feed ON feed.at >= weeks.w AND feed.at < weeks.w + INTERVAL 1 WEEK
 GROUP BY weeks.w ORDER BY weeks.w;

-- ---------------------------------------------------------
-- Q14 [JOIN + GROUP BY + conditional COUNT] A user's tasks per project, open vs done
-- used by: GET /users/me/insights → tasks_by_project   (BASE_TASKS_BY_PROJECT), dashboard bar chart
-- ---------------------------------------------------------
SET @uid = 7;
SELECT p.p_name,
       COUNT(CASE WHEN tk.status <> 'Done' THEN 1 END) AS open_tasks,
       COUNT(CASE WHEN tk.status = 'Done' THEN 1 END) AS done_tasks
  FROM Task tk JOIN Project p ON p.p_id = tk.p_id
 WHERE tk.u_id = @uid
 GROUP BY p.p_id, p.p_name ORDER BY COUNT(*) DESC, p.p_name LIMIT 8;
