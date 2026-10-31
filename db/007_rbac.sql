-- =========================================================
-- Role-based access control in the database (rubric 12).
-- Applied as root. ${...} placeholders are substituted from .env by migrate.py.
--
--   tt_admin       full control (DBA / maintenance)
--   tt_member_app  what the API runs as: read everything, write only where safe;
--                  guarded changes go through DEFINER procedures (004)
--   tt_analyst     read-only reporting on views
-- =========================================================
USE teamtree;

CREATE ROLE IF NOT EXISTS 'tt_admin', 'tt_member_app', 'tt_analyst';

GRANT ALL PRIVILEGES ON teamtree.* TO 'tt_admin';

-- Application role
GRANT SELECT, EXECUTE ON teamtree.* TO 'tt_member_app';
GRANT INSERT, UPDATE, DELETE ON teamtree.user_has_skill TO 'tt_member_app';
GRANT INSERT, UPDATE, DELETE ON teamtree.Requires       TO 'tt_member_app';
GRANT INSERT, DELETE         ON teamtree.Domain         TO 'tt_member_app';
GRANT INSERT, UPDATE         ON teamtree.Task           TO 'tt_member_app';
-- Column-level privileges: owner_id changes only via transfer_ownership,
-- role/is_active only via set_user_role/deactivate_user.
GRANT UPDATE (p_name, description, deadline, status, max_team_size) ON teamtree.Project TO 'tt_member_app';
GRANT UPDATE (f_name, m_name, l_name, bio, location, u_photo, dob,
              experience_level, availability, password_hash) ON teamtree.Users TO 'tt_member_app';
-- Deliberately NOT granted: any write on Application, Joins, Team, Skill,
-- Ownership_Transfer, and INSERT on Users/Project (register_user, create_project).

-- Read-only reporting role: views only
GRANT SELECT ON teamtree.OpenProjects              TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectListing            TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectApplicationSummary TO 'tt_analyst';
GRANT SELECT ON teamtree.TopInDemandSkills         TO 'tt_analyst';
GRANT SELECT ON teamtree.TaskProgressSummary       TO 'tt_analyst';
GRANT SELECT ON teamtree.SkillGap                  TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectSkillRequirements  TO 'tt_analyst';

-- Login users bound to roles
CREATE USER IF NOT EXISTS 'tt_app'@'%'    IDENTIFIED BY '${TT_APP_PASSWORD}';
CREATE USER IF NOT EXISTS 'tt_report'@'%' IDENTIFIED BY '${TT_REPORT_PASSWORD}';
ALTER USER 'tt_app'@'%'    IDENTIFIED BY '${TT_APP_PASSWORD}';
ALTER USER 'tt_report'@'%' IDENTIFIED BY '${TT_REPORT_PASSWORD}';

GRANT 'tt_member_app' TO 'tt_app'@'%';
GRANT 'tt_analyst'    TO 'tt_report'@'%';
SET DEFAULT ROLE 'tt_member_app' TO 'tt_app'@'%';
SET DEFAULT ROLE 'tt_analyst'    TO 'tt_report'@'%';
