-- =========================================================
-- Role-based access control in the database (rubric 12).
-- Applied as root. ${...} placeholders are substituted from .env by migrate.py.
--
--   tt_admin       full control (DBA / maintenance)
--   tt_member_app  what the API runs as: read everything, write only where safe;
--                  guarded changes go through DEFINER procedures (004)
--   tt_analyst     read-only reporting on views
--
-- The file is a full reset of privileges: GRANT only ever adds, and dropping a
-- table does not remove its rows from mysql.tables_priv, so everything is
-- revoked first and then granted explicitly.
-- =========================================================
USE teamtree;

CREATE ROLE IF NOT EXISTS 'tt_admin', 'tt_member_app', 'tt_analyst';
CREATE USER IF NOT EXISTS 'tt_app'@'%'    IDENTIFIED BY '${TT_APP_PASSWORD}';
CREATE USER IF NOT EXISTS 'tt_report'@'%' IDENTIFIED BY '${TT_REPORT_PASSWORD}';
ALTER USER 'tt_app'@'%'    IDENTIFIED BY '${TT_APP_PASSWORD}';
ALTER USER 'tt_report'@'%' IDENTIFIED BY '${TT_REPORT_PASSWORD}';

REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'tt_admin', 'tt_member_app', 'tt_analyst';
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'tt_app'@'%', 'tt_report'@'%';

GRANT ALL PRIVILEGES ON teamtree.* TO 'tt_admin';

-- ---------- Application role ----------
GRANT SELECT ON teamtree.* TO 'tt_member_app';
GRANT INSERT, UPDATE, DELETE ON teamtree.user_has_skill TO 'tt_member_app';
GRANT INSERT, UPDATE, DELETE ON teamtree.Requires       TO 'tt_member_app';
-- Tasks: insert, and update only the editable columns (not p_id / parent_task_id).
GRANT INSERT ON teamtree.Task TO 'tt_member_app';
GRANT UPDATE (t_name, description, status, priority, due_date, u_id) ON teamtree.Task TO 'tt_member_app';
-- Column-level privileges: owner_id changes only via transfer_ownership,
-- role/is_active only via set_user_role/deactivate_user.
GRANT UPDATE (p_name, description, deadline, status, max_team_size) ON teamtree.Project TO 'tt_member_app';
GRANT UPDATE (f_name, m_name, l_name, bio, location, u_photo, dob,
              experience_level, availability, password_hash) ON teamtree.Users TO 'tt_member_app';
-- Not granted: any write on Application, Joins, Team, Skill, Domain, Ownership_Transfer,
-- and INSERT on Users/Project. Those go through the procedures below.

-- EXECUTE per routine (validate_task is trigger-internal and deliberately excluded).
GRANT EXECUTE ON PROCEDURE teamtree.register_user        TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.set_user_role        TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.deactivate_user      TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.create_skill         TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.update_skill         TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.create_project       TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.set_project_domains  TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.close_project        TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.transfer_ownership   TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.apply_to_project     TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.decide_application   TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.withdraw_application TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.assign_task          TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.remove_member        TO 'tt_member_app';
GRANT EXECUTE ON PROCEDURE teamtree.leave_team           TO 'tt_member_app';
GRANT EXECUTE ON FUNCTION  teamtree.fn_level_ord           TO 'tt_member_app';
GRANT EXECUTE ON FUNCTION  teamtree.fn_is_active_member    TO 'tt_member_app';
GRANT EXECUTE ON FUNCTION  teamtree.fn_active_member_count TO 'tt_member_app';
GRANT EXECUTE ON FUNCTION  teamtree.fn_acceptance_rate     TO 'tt_member_app';
GRANT EXECUTE ON FUNCTION  teamtree.fn_is_admin            TO 'tt_member_app';

-- ---------- Read-only reporting role: views only ----------
GRANT SELECT ON teamtree.OpenProjects              TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectListing            TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectApplicationSummary TO 'tt_analyst';
GRANT SELECT ON teamtree.TopInDemandSkills         TO 'tt_analyst';
GRANT SELECT ON teamtree.TaskProgressSummary       TO 'tt_analyst';
GRANT SELECT ON teamtree.SkillGap                  TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectSkillRequirements  TO 'tt_analyst';

-- ---------- Login users bound to roles ----------
GRANT 'tt_member_app' TO 'tt_app'@'%';
GRANT 'tt_analyst'    TO 'tt_report'@'%';
SET DEFAULT ROLE 'tt_member_app' TO 'tt_app'@'%';
SET DEFAULT ROLE 'tt_analyst'    TO 'tt_report'@'%';
