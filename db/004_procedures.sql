-- =========================================================
-- Stored procedures (rubric 8, design doc 16).
-- Created by root with the default SQL SECURITY DEFINER. The low-privilege
-- app user (tt_app) has no direct write access to Application, Joins, Team,
-- Skill, Ownership_Transfer or Users.role, so these procedures are the only
-- way to change them. Each one checks the acting user (p_actor).
-- =========================================================
USE teamtree;

DROP PROCEDURE IF EXISTS register_user;
DROP PROCEDURE IF EXISTS create_project;
DROP PROCEDURE IF EXISTS apply_to_project;
DROP PROCEDURE IF EXISTS decide_application;
DROP PROCEDURE IF EXISTS withdraw_application;
DROP PROCEDURE IF EXISTS assign_task;
DROP PROCEDURE IF EXISTS remove_member;
DROP PROCEDURE IF EXISTS leave_team;
DROP PROCEDURE IF EXISTS transfer_ownership;
DROP PROCEDURE IF EXISTS create_skill;
DROP PROCEDURE IF EXISTS update_skill;
DROP PROCEDURE IF EXISTS set_user_role;
DROP PROCEDURE IF EXISTS deactivate_user;

DELIMITER $$

-- ---------------------------------------------------------
-- Users
-- ---------------------------------------------------------
CREATE PROCEDURE register_user(IN p_f VARCHAR(50), IN p_m VARCHAR(50), IN p_l VARCHAR(50),
                               IN p_email VARCHAR(150), IN p_hash VARCHAR(255), OUT p_id INT)
BEGIN
    INSERT INTO Users (f_name, m_name, l_name, email, password_hash, role)
    VALUES (TRIM(p_f), NULLIF(TRIM(p_m), ''), TRIM(p_l), LOWER(TRIM(p_email)), p_hash, 'member');
    SET p_id = LAST_INSERT_ID();
END$$

CREATE PROCEDURE set_user_role(IN p_actor INT, IN p_user INT, IN p_role VARCHAR(10))
BEGIN
    DECLARE v_old VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    IF NOT fn_is_admin(p_actor) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_ADMIN'; END IF;
    IF p_role NOT IN ('admin','member') THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'BAD_ROLE'; END IF;

    START TRANSACTION;
    SELECT role INTO v_old FROM Users WHERE id = p_user FOR UPDATE;
    IF v_old IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'USER_NOT_FOUND'; END IF;
    IF v_old = 'admin' AND p_role = 'member' AND
       (SELECT COUNT(*) FROM Users WHERE role = 'admin' AND is_active) <= 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'LAST_ADMIN';
    END IF;
    UPDATE Users SET role = p_role WHERE id = p_user;
    COMMIT;
END$$

-- Soft delete (design doc 13.13): close Open projects, withdraw pending
-- applications, end memberships in other teams and unassign their open tasks.
CREATE PROCEDURE deactivate_user(IN p_actor INT, IN p_user INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    IF p_actor <> p_user AND NOT fn_is_admin(p_actor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_ADMIN';
    END IF;

    START TRANSACTION;
    IF NOT EXISTS (SELECT 1 FROM Users WHERE id = p_user AND is_active) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'USER_NOT_FOUND';
    END IF;
    IF fn_is_admin(p_user) AND (SELECT COUNT(*) FROM Users WHERE role = 'admin' AND is_active) <= 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'LAST_ADMIN';
    END IF;
    IF EXISTS (SELECT 1 FROM Project WHERE owner_id = p_user AND status = 'Ongoing') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'OWNS_ONGOING_PROJECTS';
    END IF;

    UPDATE Project SET status = 'Closed' WHERE owner_id = p_user AND status = 'Open';
    UPDATE Application SET status = 'Withdrawn' WHERE applicant_id = p_user AND status = 'Pending';
    UPDATE Task SET u_id = NULL WHERE u_id = p_user AND status <> 'Done';
    UPDATE Joins SET leave_date = CURDATE() WHERE u_id = p_user AND leave_date IS NULL;
    UPDATE Users SET is_active = FALSE WHERE id = p_user;
    COMMIT;
END$$

-- ---------------------------------------------------------
-- Skills (admin-managed catalogue)
-- ---------------------------------------------------------
CREATE PROCEDURE create_skill(IN p_actor INT, IN p_name VARCHAR(100), IN p_category VARCHAR(100),
                              OUT p_s_id INT)
BEGIN
    IF NOT fn_is_admin(p_actor) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_ADMIN'; END IF;
    INSERT INTO Skill (s_name, category) VALUES (TRIM(p_name), NULLIF(TRIM(p_category), ''));
    SET p_s_id = LAST_INSERT_ID();
END$$

CREATE PROCEDURE update_skill(IN p_actor INT, IN p_s_id INT, IN p_name VARCHAR(100),
                              IN p_category VARCHAR(100))
BEGIN
    IF NOT fn_is_admin(p_actor) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_ADMIN'; END IF;
    UPDATE Skill SET s_name   = COALESCE(NULLIF(TRIM(p_name), ''), s_name),
                     category = COALESCE(NULLIF(TRIM(p_category), ''), category)
     WHERE s_id = p_s_id;
    IF ROW_COUNT() = 0 AND NOT EXISTS (SELECT 1 FROM Skill WHERE s_id = p_s_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'SKILL_NOT_FOUND';
    END IF;
END$$

-- ---------------------------------------------------------
-- Projects
-- ---------------------------------------------------------
-- Project + its team + the owner's membership, atomically (owner policy: auto-member).
CREATE PROCEDURE create_project(IN p_owner INT, IN p_name VARCHAR(150), IN p_desc TEXT,
                                IN p_deadline DATE, IN p_max_size INT, OUT p_id INT)
BEGIN
    DECLARE v_tid INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE id = p_owner AND is_active) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'USER_INACTIVE';
    END IF;

    START TRANSACTION;
    INSERT INTO Project (owner_id, p_name, description, deadline, max_team_size)
    VALUES (p_owner, TRIM(p_name), p_desc, p_deadline, p_max_size);
    SET p_id = LAST_INSERT_ID();
    INSERT INTO Team (p_id, team_name) VALUES (p_id, LEFT(CONCAT(TRIM(p_name), ' Team'), 150));
    SET v_tid = LAST_INSERT_ID();
    INSERT INTO Joins (t_id, u_id, role, join_date) VALUES (v_tid, p_owner, 'Owner', CURDATE());
    COMMIT;
END$$

-- New owner must be an active member; roles are swapped and the transfer audited.
CREATE PROCEDURE transfer_ownership(IN p_pid INT, IN p_actor INT, IN p_new_owner INT)
BEGIN
    DECLARE v_owner, v_tid INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    START TRANSACTION;
    SELECT owner_id INTO v_owner FROM Project WHERE p_id = p_pid FOR UPDATE;
    IF v_owner IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_FOUND'; END IF;
    IF v_owner <> p_actor THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_OWNER'; END IF;
    IF p_new_owner = p_actor OR NOT fn_is_active_member(p_pid, p_new_owner) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_ACTIVE_MEMBER';
    END IF;

    SELECT t_id INTO v_tid FROM Team WHERE p_id = p_pid;
    UPDATE Project SET owner_id = p_new_owner WHERE p_id = p_pid;
    UPDATE Joins SET role = 'Member' WHERE t_id = v_tid AND u_id = p_actor     AND leave_date IS NULL;
    UPDATE Joins SET role = 'Owner'  WHERE t_id = v_tid AND u_id = p_new_owner AND leave_date IS NULL;
    INSERT INTO Ownership_Transfer (p_id, from_user, to_user) VALUES (p_pid, p_actor, p_new_owner);
    COMMIT;
END$$

-- ---------------------------------------------------------
-- Applications
-- ---------------------------------------------------------
-- Validation lives in trg_application_bi and uq_application_pending.
CREATE PROCEDURE apply_to_project(IN p_user INT, IN p_pid INT, IN p_msg TEXT, OUT p_a_id INT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Users WHERE id = p_user AND is_active) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'USER_INACTIVE';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Project WHERE p_id = p_pid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_FOUND';
    END IF;
    -- The owner is also a team member; report the more specific reason first.
    IF EXISTS (SELECT 1 FROM Project WHERE p_id = p_pid AND owner_id = p_user) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'SELF_APPLICATION';
    END IF;
    IF fn_is_active_member(p_pid, p_user) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ALREADY_MEMBER';
    END IF;
    INSERT INTO Application (applicant_id, p_id, msg) VALUES (p_user, p_pid, p_msg);
    SET p_a_id = LAST_INSERT_ID();
END$$

-- Design doc 16.1: accept = status + decision date + team membership, atomically.
-- The project row is locked first so concurrent accepts cannot exceed capacity.
CREATE PROCEDURE decide_application(IN p_a_id INT, IN p_actor INT,
                                    IN p_decision VARCHAR(10), IN p_role VARCHAR(100))
BEGIN
    DECLARE v_pid, v_applicant, v_owner, v_cap, v_tid INT;
    DECLARE v_status, v_pstatus VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    IF p_decision NOT IN ('Accepted','Rejected') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'BAD_DECISION';
    END IF;

    START TRANSACTION;
    SELECT p_id INTO v_pid FROM Application WHERE a_id = p_a_id;
    IF v_pid IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_FOUND'; END IF;

    SELECT owner_id, status, max_team_size INTO v_owner, v_pstatus, v_cap
      FROM Project WHERE p_id = v_pid FOR UPDATE;
    SELECT applicant_id, status INTO v_applicant, v_status
      FROM Application WHERE a_id = p_a_id FOR UPDATE;

    IF v_owner <> p_actor    THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_OWNER';       END IF;
    IF v_status <> 'Pending' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_PENDING'; END IF;

    IF p_decision = 'Accepted' THEN
        IF v_pstatus NOT IN ('Open','Ongoing') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_ACCEPTING';
        END IF;
        IF v_cap IS NOT NULL AND fn_active_member_count(v_pid) >= v_cap THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_FULL';
        END IF;
        SELECT t_id INTO v_tid FROM Team WHERE p_id = v_pid;
        INSERT INTO Joins (t_id, u_id, role, join_date)
        VALUES (v_tid, v_applicant, COALESCE(NULLIF(TRIM(p_role), ''), 'Member'), CURDATE());
    END IF;

    UPDATE Application SET status = p_decision, decision_date = NOW() WHERE a_id = p_a_id;
    COMMIT;
END$$

CREATE PROCEDURE withdraw_application(IN p_a_id INT, IN p_actor INT)
BEGIN
    DECLARE v_applicant INT;
    DECLARE v_status VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    START TRANSACTION;
    SELECT applicant_id, status INTO v_applicant, v_status
      FROM Application WHERE a_id = p_a_id FOR UPDATE;
    IF v_applicant IS NULL     THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_FOUND';   END IF;
    IF v_applicant <> p_actor  THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_APPLICANT';   END IF;
    IF v_status <> 'Pending'   THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_PENDING'; END IF;
    UPDATE Application SET status = 'Withdrawn' WHERE a_id = p_a_id;
    COMMIT;
END$$

-- ---------------------------------------------------------
-- Teams & tasks
-- ---------------------------------------------------------
-- Actor must be the owner or an active member; trg_task_bu validates the assignee.
CREATE PROCEDURE assign_task(IN p_task_id INT, IN p_actor INT, IN p_assignee INT)
BEGIN
    DECLARE v_pid INT;
    SELECT p_id INTO v_pid FROM Task WHERE task_id = p_task_id;
    IF v_pid IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TASK_NOT_FOUND'; END IF;
    IF NOT fn_is_active_member(v_pid, p_actor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_MEMBER';
    END IF;
    UPDATE Task SET u_id = p_assignee WHERE task_id = p_task_id;
END$$

-- Owner removes a member, or a member removes themselves (leave_team).
-- History is kept (leave_date). Their unfinished tasks become unassigned (13.9).
CREATE PROCEDURE remove_member(IN p_pid INT, IN p_actor INT, IN p_user INT)
BEGIN
    DECLARE v_owner, v_tid INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    START TRANSACTION;
    SELECT owner_id INTO v_owner FROM Project WHERE p_id = p_pid FOR UPDATE;
    IF v_owner IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_FOUND'; END IF;
    IF p_actor <> v_owner AND p_actor <> p_user THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_OWNER';
    END IF;
    IF p_user = v_owner THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'OWNER_CANNOT_LEAVE'; END IF;
    IF NOT fn_is_active_member(p_pid, p_user) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_ACTIVE_MEMBER';
    END IF;

    SELECT t_id INTO v_tid FROM Team WHERE p_id = p_pid;
    UPDATE Task SET u_id = NULL WHERE p_id = p_pid AND u_id = p_user AND status <> 'Done';
    UPDATE Joins SET leave_date = CURDATE() WHERE t_id = v_tid AND u_id = p_user AND leave_date IS NULL;
    COMMIT;
END$$

CREATE PROCEDURE leave_team(IN p_pid INT, IN p_user INT)
BEGIN
    CALL remove_member(p_pid, p_user, p_user);
END$$

DELIMITER ;
