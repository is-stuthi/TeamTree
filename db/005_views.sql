-- =========================================================
-- Views (rubric 7/8). Derived values (overdue, team size, rates, gaps)
-- are computed here, never stored.
-- =========================================================
USE teamtree;

-- All projects with owner, domains, required skills and derived fields
CREATE OR REPLACE VIEW ProjectListing AS
SELECT p.p_id, p.p_name, p.description, p.deadline, p.status, p.max_team_size, p.creation_date,
       p.owner_id, CONCAT(u.f_name, ' ', u.l_name) AS owner_name,
       (SELECT GROUP_CONCAT(d.d_name ORDER BY d.d_name SEPARATOR ',')
          FROM Domain d WHERE d.project_id = p.p_id) AS domains,
       (SELECT GROUP_CONCAT(DISTINCT s.s_name ORDER BY s.s_name SEPARATOR ',')
          FROM Requires r JOIN Skill s ON s.s_id = r.s_id WHERE r.p_id = p.p_id) AS required_skills,
       fn_active_member_count(p.p_id) AS team_size,
       (p.deadline IS NOT NULL AND p.deadline < CURDATE()
        AND p.status IN ('Open','Ongoing')) AS is_overdue
FROM Project p
JOIN Users u ON u.id = p.owner_id;

CREATE OR REPLACE VIEW OpenProjects AS
SELECT * FROM ProjectListing WHERE status = 'Open';

CREATE OR REPLACE VIEW ProjectApplicationSummary AS
SELECT p.p_id, p.p_name, p.owner_id,
       COUNT(a.a_id)                          AS total_applications,
       COALESCE(SUM(a.status = 'Pending'), 0)   AS pending,
       COALESCE(SUM(a.status = 'Accepted'), 0)  AS accepted,
       COALESCE(SUM(a.status = 'Rejected'), 0)  AS rejected,
       COALESCE(SUM(a.status = 'Withdrawn'), 0) AS withdrawn,
       fn_acceptance_rate(p.p_id)             AS acceptance_rate
FROM Project p
LEFT JOIN Application a ON a.p_id = p.p_id
GROUP BY p.p_id, p.p_name, p.owner_id;

CREATE OR REPLACE VIEW UserSkillProfiles AS
SELECT u.id AS u_id, CONCAT(u.f_name, ' ', u.l_name) AS user_name,
       s.s_id, s.s_name, s.category, h.u_s_level, fn_level_ord(h.u_s_level) AS level_ord
FROM Users u
JOIN user_has_skill h ON h.u_id = u.id
JOIN Skill s          ON s.s_id = h.s_id
WHERE u.is_active;

CREATE OR REPLACE VIEW ProjectSkillRequirements AS
SELECT r.p_id, p.p_name, r.s_id, s.s_name, s.category, r.req_role,
       r.p_s_level, fn_level_ord(r.p_s_level) AS level_ord, r.req_count
FROM Requires r
JOIN Project p ON p.p_id = r.p_id
JOIN Skill s   ON s.s_id = r.s_id;

-- Active and past members (history is preserved)
CREATE OR REPLACE VIEW TeamMemberDetails AS
SELECT t.p_id, t.t_id, t.team_name, j.j_id, j.u_id,
       CONCAT(u.f_name, ' ', u.l_name) AS member_name, u.email,
       j.role, j.join_date, j.leave_date, (j.leave_date IS NULL) AS is_active
FROM Team t
JOIN Joins j ON j.t_id = t.t_id
JOIN Users u ON u.id = j.u_id;

CREATE OR REPLACE VIEW TaskProgressSummary AS
SELECT p.p_id, p.p_name,
       COUNT(tk.task_id)                               AS total_tasks,
       COALESCE(SUM(tk.status = 'To Do'), 0)           AS todo,
       COALESCE(SUM(tk.status = 'In Progress'), 0)     AS in_progress,
       COALESCE(SUM(tk.status = 'Done'), 0)            AS done,
       COALESCE(SUM(tk.status = 'Blocked'), 0)         AS blocked,
       ROUND(100 * SUM(tk.status = 'Done') / NULLIF(COUNT(tk.task_id), 0), 1) AS pct_done,
       COALESCE(SUM(tk.due_date < CURDATE() AND tk.status <> 'Done'), 0) AS overdue_tasks
FROM Project p
LEFT JOIN Task tk ON tk.p_id = p.p_id
GROUP BY p.p_id, p.p_name;

-- CTE + window function: demand vs supply per skill
CREATE OR REPLACE VIEW TopInDemandSkills AS
WITH demand AS (SELECT s_id, COUNT(DISTINCT p_id) AS projects_requiring FROM Requires GROUP BY s_id),
     supply AS (SELECT s_id, COUNT(*) AS users_possessing FROM user_has_skill GROUP BY s_id)
SELECT s.s_id, s.s_name, s.category,
       COALESCE(d.projects_requiring, 0) AS projects_requiring,
       COALESCE(u.users_possessing, 0)   AS users_possessing,
       ROUND(COALESCE(d.projects_requiring, 0) / NULLIF(u.users_possessing, 0), 2) AS demand_supply_ratio,
       RANK() OVER (ORDER BY COALESCE(d.projects_requiring, 0) DESC) AS demand_rank
FROM Skill s
LEFT JOIN demand d ON d.s_id = s.s_id
LEFT JOIN supply u ON u.s_id = s.s_id;

-- Required skill vs active members who meet the required level (design doc 10.1)
CREATE OR REPLACE VIEW SkillGap AS
SELECT r.p_id, r.s_id, s.s_name, r.req_role, r.p_s_level AS required_level, r.req_count,
       COUNT(DISTINCT h.u_id) AS members_with_skill,
       COUNT(DISTINCT CASE WHEN fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)
                           THEN h.u_id END) AS qualified_members,
       GREATEST(r.req_count - COUNT(DISTINCT CASE WHEN fn_level_ord(h.u_s_level)
                >= fn_level_ord(r.p_s_level) THEN h.u_id END), 0) AS shortfall
FROM Requires r
JOIN Skill s               ON s.s_id = r.s_id
LEFT JOIN Team t           ON t.p_id = r.p_id
LEFT JOIN Joins j          ON j.t_id = t.t_id AND j.leave_date IS NULL
LEFT JOIN user_has_skill h ON h.u_id = j.u_id AND h.s_id = r.s_id
GROUP BY r.p_id, r.s_id, s.s_name, r.req_role, r.p_s_level, r.req_count;
