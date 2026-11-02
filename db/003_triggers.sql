-- =========================================================
-- Triggers (rubric 8). Validation only: they never write other rows.
-- Errors use SIGNAL SQLSTATE '45000' with a stable code mapped in api/app/errors.py.
-- =========================================================
USE teamtree;

DROP TRIGGER IF EXISTS trg_application_bi;
DROP TRIGGER IF EXISTS trg_task_bi;
DROP TRIGGER IF EXISTS trg_task_bu;
DROP TRIGGER IF EXISTS trg_project_bu;
DROP PROCEDURE IF EXISTS validate_task;

DELIMITER $$

-- Applications only to Open projects, never to your own, never when full.
-- Advisory at insert time; decide_application re-checks under the Project lock.
CREATE TRIGGER trg_application_bi BEFORE INSERT ON Application
FOR EACH ROW
BEGIN
    DECLARE v_owner INT;
    DECLARE v_status VARCHAR(10);
    DECLARE v_cap INT;

    SELECT owner_id, status, max_team_size INTO v_owner, v_status, v_cap
      FROM Project WHERE p_id = NEW.p_id;

    IF v_status <> 'Open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_OPEN';
    END IF;
    IF v_owner = NEW.applicant_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'SELF_APPLICATION';
    END IF;
    IF v_cap IS NOT NULL AND fn_active_member_count(NEW.p_id) >= v_cap THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_FULL';
    END IF;
END$$

-- Shared task validation. NULL arguments mean "not changing, don't check", so
-- the UPDATE trigger only re-validates columns that actually changed.
CREATE PROCEDURE validate_task(IN p_pid INT, IN p_uid INT, IN p_due DATE, IN p_parent INT)
BEGIN
    DECLARE v_deadline DATE;
    IF p_uid IS NOT NULL AND NOT fn_is_active_member(p_pid, p_uid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ASSIGNEE_NOT_MEMBER';
    END IF;
    SELECT deadline INTO v_deadline FROM Project WHERE p_id = p_pid;
    IF p_due IS NOT NULL AND v_deadline IS NOT NULL AND p_due > v_deadline THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TASK_AFTER_DEADLINE';
    END IF;
    IF p_parent IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Task WHERE task_id = p_parent AND p_id = p_pid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PARENT_OTHER_PROJECT';
    END IF;
END$$

CREATE TRIGGER trg_task_bi BEFORE INSERT ON Task
FOR EACH ROW
BEGIN
    IF (SELECT status FROM Project WHERE p_id = NEW.p_id) IN ('Completed','Closed') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_FINISHED';
    END IF;
    CALL validate_task(NEW.p_id, NEW.u_id, NEW.due_date, NEW.parent_task_id);
END$$

-- Only changed columns are re-checked: a Done task whose assignee later left,
-- or a task due after a since-moved deadline, can still be edited/blocked.
-- (p_id and parent_task_id are not updatable by tt_app: column-level GRANT.)
CREATE TRIGGER trg_task_bu BEFORE UPDATE ON Task
FOR EACH ROW
CALL validate_task(NEW.p_id,
                   IF(NEW.u_id <=> OLD.u_id, NULL, NEW.u_id),
                   IF(NEW.due_date <=> OLD.due_date, NULL, NEW.due_date),
                   IF(NEW.parent_task_id <=> OLD.parent_task_id, NULL, NEW.parent_task_id))$$

-- Lifecycle guard and consistency of owner edits.
CREATE TRIGGER trg_project_bu BEFORE UPDATE ON Project
FOR EACH ROW
BEGIN
    IF OLD.status IN ('Completed','Closed') AND NEW.status IN ('Open','Ongoing') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_REOPEN_FORBIDDEN';
    END IF;
    IF NEW.max_team_size IS NOT NULL AND NOT (NEW.max_team_size <=> OLD.max_team_size)
       AND NEW.max_team_size < fn_active_member_count(NEW.p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CAPACITY_BELOW_TEAM';
    END IF;
    IF NEW.deadline IS NOT NULL AND NOT (NEW.deadline <=> OLD.deadline)
       AND EXISTS (SELECT 1 FROM Task WHERE p_id = NEW.p_id AND status <> 'Done' AND due_date > NEW.deadline) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'DEADLINE_BEFORE_TASKS';
    END IF;
END$$

DELIMITER ;
