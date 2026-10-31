-- =========================================================
-- Secondary indexes, chosen from the actual search and join patterns.
-- PK/UNIQUE keys (email, s_name_norm, Team.p_id) are already indexed.
-- Composite indexes whose leading column is an FK replace the implicit FK index.
-- =========================================================
USE teamtree;

CREATE INDEX ix_users_name       ON Users (l_name, f_name);
CREATE INDEX ix_project_status   ON Project (status, deadline);
CREATE INDEX ix_domain_name      ON Domain (d_name);
CREATE INDEX ix_requires_skill   ON Requires (s_id, p_s_level);
CREATE INDEX ix_uhs_skill        ON user_has_skill (s_id, u_s_level);
CREATE INDEX ix_application_proj ON Application (p_id, status);
CREATE INDEX ix_task_project     ON Task (p_id, status);
CREATE INDEX ix_task_user        ON Task (u_id, status);
CREATE INDEX ix_joins_user       ON Joins (u_id, leave_date);
