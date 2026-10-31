-- =========================================================
-- Stored functions (rubric 8). Loaded before triggers/views that use them.
-- =========================================================
USE teamtree;

DROP FUNCTION IF EXISTS fn_level_ord;
DROP FUNCTION IF EXISTS fn_is_active_member;
DROP FUNCTION IF EXISTS fn_active_member_count;
DROP FUNCTION IF EXISTS fn_acceptance_rate;
DROP FUNCTION IF EXISTS fn_is_admin;

DELIMITER $$

-- Proficiency ordinal: Beginner=1 ... Expert=4 (0 for NULL/unknown)
CREATE FUNCTION fn_level_ord(lvl VARCHAR(20)) RETURNS TINYINT
DETERMINISTIC NO SQL
RETURN CASE lvl WHEN 'Beginner' THEN 1 WHEN 'Intermediate' THEN 2
                WHEN 'Advanced' THEN 3 WHEN 'Expert' THEN 4 ELSE 0 END$$

-- Is the user an active member of the project's team?
CREATE FUNCTION fn_is_active_member(p_pid INT, p_uid INT) RETURNS BOOLEAN
READS SQL DATA
RETURN EXISTS (SELECT 1 FROM Joins j JOIN Team t ON t.t_id = j.t_id
                WHERE t.p_id = p_pid AND j.u_id = p_uid AND j.leave_date IS NULL)$$

-- Number of active members (owner included)
CREATE FUNCTION fn_active_member_count(p_pid INT) RETURNS INT
READS SQL DATA
RETURN (SELECT COUNT(*) FROM Joins j JOIN Team t ON t.t_id = j.t_id
         WHERE t.p_id = p_pid AND j.leave_date IS NULL)$$

-- Accepted / decided. Pending and Withdrawn are excluded from the denominator.
CREATE FUNCTION fn_acceptance_rate(p_pid INT) RETURNS DECIMAL(5,4)
READS SQL DATA
RETURN (SELECT SUM(status = 'Accepted') / NULLIF(SUM(status IN ('Accepted','Rejected')), 0)
          FROM Application WHERE p_id = p_pid)$$

CREATE FUNCTION fn_is_admin(p_uid INT) RETURNS BOOLEAN
READS SQL DATA
RETURN EXISTS (SELECT 1 FROM Users WHERE id = p_uid AND role = 'admin' AND is_active)$$

DELIMITER ;
