"""SQL for analytics (design doc §11). VIEW_* run as tt_report (views only);
BASE_* need base tables and run as tt_app. Rubric-labelled queries are mirrored
in db/queries/catalogue.sql."""

# ---------- views (tt_report) ----------
VIEW_SKILL_DEMAND = """SELECT s_name, category, projects_requiring, users_possessing, demand_supply_ratio, demand_rank
                         FROM TopInDemandSkills WHERE projects_requiring > 0 OR users_possessing > 0
                        ORDER BY projects_requiring DESC, users_possessing DESC, s_name LIMIT 12"""

# Q10 [CTE + WINDOW] top 3 in-demand skills per category
VIEW_TOP_BY_CATEGORY = """WITH ranked AS (
    SELECT category, s_name, projects_requiring,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY projects_requiring DESC, s_name) AS rn
      FROM TopInDemandSkills WHERE projects_requiring > 0)
SELECT category, s_name, projects_requiring, rn AS rank_in_category
  FROM ranked WHERE rn <= 3 ORDER BY category, rn"""

VIEW_BY_STATUS = "SELECT status, COUNT(*) AS n FROM ProjectListing GROUP BY status"

VIEW_APPROACHING = """SELECT p_name, status, deadline, DATEDIFF(deadline, CURDATE()) AS days_left
                        FROM ProjectListing
                       WHERE status IN ('Open','Ongoing') AND deadline IS NOT NULL
                         AND deadline BETWEEN CURDATE() AND CURDATE() + INTERVAL 30 DAY
                       ORDER BY deadline"""

VIEW_AVG_DURATION = """SELECT ROUND(AVG(DATEDIFF(deadline, DATE(creation_date))), 1) AS days
                         FROM ProjectListing WHERE status = 'Completed' AND deadline IS NOT NULL"""

VIEW_APP_SUMMARY = """SELECT p_name, total_applications, pending, accepted, rejected, withdrawn, acceptance_rate
                        FROM ProjectApplicationSummary ORDER BY total_applications DESC, p_name"""

VIEW_TEAM_SIZES = """SELECT p_name, status, team_size FROM ProjectListing ORDER BY team_size DESC, p_name"""

VIEW_TASK_PROGRESS = """SELECT p_name, total_tasks, done, in_progress, todo, blocked, pct_done, overdue_tasks
                          FROM TaskProgressSummary WHERE total_tasks > 0 ORDER BY pct_done DESC, p_name"""

# ---------- base tables (tt_app) ----------
BASE_BY_DOMAIN = "SELECT d_name AS domain, COUNT(*) AS n FROM Domain GROUP BY d_name ORDER BY n DESC, domain LIMIT 10"

# Q2 [LEFT JOIN + GROUP BY + HAVING] projects that have received no applications
BASE_NO_APPLICATIONS = """SELECT p.p_id, p.p_name, p.status, COUNT(a.a_id) AS applications
                            FROM Project p LEFT JOIN Application a ON a.p_id = p.p_id
                           GROUP BY p.p_id, p.p_name, p.status
                          HAVING COUNT(a.a_id) = 0 ORDER BY p.p_name"""

BASE_AVG_DECISION_DAYS = """SELECT ROUND(AVG(TIMESTAMPDIFF(HOUR, a_date, decision_date)) / 24, 1) AS days
                              FROM Application WHERE decision_date IS NOT NULL"""

# Q9 [RECURSIVE CTE: date series] applications per day for the last 30 days, gaps filled with 0
# Executed WITHOUT params, so '%' is literal here (aiomysql only %-formats when args are given).
BASE_TIMELINE = """WITH RECURSIVE days AS (
    SELECT CURDATE() - INTERVAL 29 DAY AS d
    UNION ALL SELECT d + INTERVAL 1 DAY FROM days WHERE d < CURDATE())
SELECT DATE_FORMAT(days.d, '%Y-%m-%d') AS day, COUNT(a.a_id) AS applications
  FROM days LEFT JOIN Application a ON DATE(a.a_date) = days.d
 GROUP BY days.d ORDER BY days.d"""

# Correlated counts per user (labelled metrics: activity is not "quality")
BASE_USER_ACTIVITY = """SELECT CONCAT(u.f_name, ' ', u.l_name) AS name,
       (SELECT COUNT(*) FROM Project p WHERE p.owner_id = u.id) AS projects_created,
       (SELECT COUNT(*) FROM Application a WHERE a.applicant_id = u.id) AS applications_submitted,
       (SELECT COUNT(*) FROM Application a WHERE a.applicant_id = u.id AND a.status = 'Accepted') AS applications_accepted,
       (SELECT COUNT(*) FROM Joins j WHERE j.u_id = u.id) AS teams_joined,
       (SELECT COUNT(*) FROM Task t WHERE t.u_id = u.id AND t.status = 'Done') AS tasks_completed
  FROM Users u WHERE u.is_active
 ORDER BY applications_submitted + teams_joined + tasks_completed DESC, name LIMIT 10"""

BASE_ROLE_DISTRIBUTION = """SELECT role, COUNT(*) AS n FROM Joins WHERE leave_date IS NULL
                             GROUP BY role ORDER BY n DESC, role LIMIT 10"""

PUBLIC_TOTALS = """SELECT (SELECT COUNT(*) FROM Users WHERE is_active) AS users,
       (SELECT COUNT(*) FROM Project WHERE status = 'Open') AS open_projects,
       (SELECT COUNT(*) FROM Team) AS teams,
       (SELECT COUNT(*) FROM Skill) AS skills,
       (SELECT COUNT(*) FROM Application WHERE status = 'Accepted') AS people_matched"""

# Q12 [UNION ALL] the current user's activity feed (also the event source for Q13)
_FEED = """
    SELECT a.a_date AS at, 'application' AS kind, CONCAT('Applied to ', p.p_name, ' (', a.status, ')') AS what
      FROM Application a JOIN Project p ON p.p_id = a.p_id WHERE a.applicant_id = %(u)s
    UNION ALL
    SELECT j.join_date, 'team', CONCAT('Joined ', t.team_name, ' as ', j.role)
      FROM Joins j JOIN Team t ON t.t_id = j.t_id WHERE j.u_id = %(u)s
    UNION ALL
    SELECT j.leave_date, 'team', CONCAT('Left ', t.team_name)
      FROM Joins j JOIN Team t ON t.t_id = j.t_id WHERE j.u_id = %(u)s AND j.leave_date IS NOT NULL
    UNION ALL
    SELECT tk.created_at, 'task', CONCAT('Task: ', tk.t_name, ' (', tk.status, ')')
      FROM Task tk WHERE tk.u_id = %(u)s
"""
BASE_ACTIVITY_FEED = f"SELECT * FROM ({_FEED}) feed ORDER BY at DESC LIMIT 15"

# Q13 [RECURSIVE CTE: week series + UNION ALL] the user's activity per week, last 12 weeks, gaps = 0
BASE_ACTIVITY_WEEKLY = f"""WITH RECURSIVE weeks AS (
    SELECT CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY - INTERVAL 11 WEEK AS w
    UNION ALL SELECT w + INTERVAL 1 WEEK FROM weeks
     WHERE w < CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY)
SELECT CAST(weeks.w AS CHAR) AS week, COUNT(feed.at) AS activity
  FROM weeks LEFT JOIN ({_FEED}) feed ON feed.at >= weeks.w AND feed.at < weeks.w + INTERVAL 1 WEEK
 GROUP BY weeks.w ORDER BY weeks.w"""

# Q14 [JOIN + GROUP BY + conditional COUNT] the user's tasks per project, open vs done
BASE_TASKS_BY_PROJECT = """SELECT p.p_name,
       COUNT(CASE WHEN tk.status <> 'Done' THEN 1 END) AS open_tasks,
       COUNT(CASE WHEN tk.status = 'Done' THEN 1 END) AS done_tasks
  FROM Task tk JOIN Project p ON p.p_id = tk.p_id
 WHERE tk.u_id = %(u)s
 GROUP BY p.p_id, p.p_name ORDER BY COUNT(*) DESC, p.p_name LIMIT 8"""
