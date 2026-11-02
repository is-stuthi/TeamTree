-- =========================================================
-- DML demo (rubric 6). NOT part of the migration.
-- Each statement: -- Dn [OPERATION] description  ·  used by: <endpoint>
-- Run as root on a fresh seed (they modify data). Under tt_app, D7-style
-- changes are only possible through the procedures.
-- =========================================================
USE teamtree;

-- D1 [MULTI-ROW INSERT + UPSERT] add several skills to a profile at once
-- used by: PUT /users/me/skills
INSERT INTO user_has_skill (u_id, s_id, u_s_level)
VALUES (6, 11, 'Beginner'), (6, 1, 'Intermediate') AS new
ON DUPLICATE KEY UPDATE u_s_level = new.u_s_level;

-- D2 [INSERT ... SELECT] copy another project's requirements ("use as template")
-- used by: POST /projects/{p_id}/requirements/copy-from/{src_p_id}
INSERT INTO Requires (p_id, s_id, req_role, p_s_level, req_count)
SELECT 8, src.s_id, src.req_role, src.p_s_level, src.req_count
  FROM Requires src WHERE src.p_id = 1
ON DUPLICATE KEY UPDATE p_s_level = src.p_s_level, req_count = src.req_count;

-- D3 [UPDATE ... JOIN] closing a project blocks its unfinished tasks
-- used by: PATCH /projects/{p_id} with status=Closed -> CALL close_project (same UPDATE ... JOIN,
--          inside one transaction that also rejects pending applications)
UPDATE Project SET status = 'Closed' WHERE p_id = 3;
UPDATE Task t JOIN Project p ON p.p_id = t.p_id
   SET t.status = 'Blocked'
 WHERE p.p_id = 3 AND p.status = 'Closed' AND t.status IN ('To Do', 'In Progress');

-- D4 [UPDATE: soft delete] deactivate an account (history is kept)
-- used by: POST /users/me/deactivate, POST /admin/users/{id}/deactivate
CALL deactivate_user(1, 12);
SELECT id, is_active FROM Users WHERE id = 12;

-- D5 [DELETE] remove a skill from a profile
-- used by: DELETE /users/me/skills/{s_id}
DELETE FROM user_has_skill WHERE u_id = 6 AND s_id = 11;

-- D6 [UPSERT] set one skill's proficiency
-- used by: PUT /users/me/skills/{s_id}
INSERT INTO user_has_skill (u_id, s_id, u_s_level) VALUES (6, 16, 'Advanced') AS new
ON DUPLICATE KEY UPDATE u_s_level = new.u_s_level;

-- D7 [TRANSACTION via procedure] accept an application: status + decision date
-- + team membership commit together, or not at all
-- used by: POST /applications/{a_id}/decision
CALL decide_application(1, 2, 'Accepted', 'Data Labeller');
SELECT a.status, a.decision_date, tm.role
  FROM Application a JOIN TeamMemberDetails tm ON tm.p_id = a.p_id AND tm.u_id = a.applicant_id
 WHERE a.a_id = 1;
