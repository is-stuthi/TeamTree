-- =========================================================
-- TeamTree Database Schema (MySQL 8.0)
-- =========================================================

CREATE DATABASE IF NOT EXISTS `teamtree`;
USE `teamtree`;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `Application`;
DROP TABLE IF EXISTS `Task`;
DROP TABLE IF EXISTS `Joins`;
DROP TABLE IF EXISTS `Team`;
DROP TABLE IF EXISTS `user_has_skill`;
DROP TABLE IF EXISTS `Requires`;
DROP TABLE IF EXISTS `Domain`;
DROP TABLE IF EXISTS `Skill`;
DROP TABLE IF EXISTS `Project`;
DROP TABLE IF EXISTS `Users`;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================================================
-- Users
-- =========================================================
CREATE TABLE `Users` (
    `id`           INT AUTO_INCREMENT,
    `f_name`       VARCHAR(50)  NOT NULL,
    `m_name`       VARCHAR(50)  NULL,
    `l_name`       VARCHAR(50)  NOT NULL,
    `email`        VARCHAR(150) NOT NULL,
    `password`     VARCHAR(255) NOT NULL,
    `bio`          TEXT         NULL,
    `location`     VARCHAR(150) NULL,
    `u_photo`      VARCHAR(255) NULL,
    `dob`          DATE         NULL,
    `availability` BOOLEAN      NOT NULL DEFAULT TRUE,
    `is_admin`     BOOLEAN      NOT NULL DEFAULT FALSE,
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- NOTE: no CHECK on dob here — MySQL disallows non-deterministic
-- functions (CURDATE()/CURRENT_DATE) inside CHECK constraints.

-- =========================================================
-- Project
-- =========================================================
CREATE TABLE `Project` (
    `p_id`          INT AUTO_INCREMENT,
    `owner_id`      INT          NOT NULL,
    `p_name`        VARCHAR(150) NOT NULL,
    `description`   TEXT         NULL,
    `deadline`      DATE         NULL,
    `status`        ENUM('Planning','Active','Completed','Cancelled') NOT NULL DEFAULT 'Planning',
    `creation_date` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`p_id`),
    CONSTRAINT `fk_project_owner`
        FOREIGN KEY (`owner_id`) REFERENCES `Users` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Domain (multivalued attribute of Project)
-- =========================================================
CREATE TABLE `Domain` (
    `project_id` INT          NOT NULL,
    `d_name`     VARCHAR(100) NOT NULL,
    PRIMARY KEY (`project_id`, `d_name`),
    CONSTRAINT `fk_domain_project`
        FOREIGN KEY (`project_id`) REFERENCES `Project` (`p_id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Skill
-- =========================================================
CREATE TABLE `Skill` (
    `s_id`     INT AUTO_INCREMENT,
    `s_name`   VARCHAR(100) NOT NULL,
    `s_domain` VARCHAR(100) NULL,
    PRIMARY KEY (`s_id`),
    UNIQUE KEY `uq_skill_name` (`s_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Requires (Project requires Skill)
-- =========================================================
CREATE TABLE `Requires` (
    `s_id`       INT         NOT NULL,
    `p_id`       INT         NOT NULL,
    `p_s_level`  ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL,
    `req_role`   VARCHAR(100) NULL,
    `req_count`  INT         NOT NULL DEFAULT 1,
    PRIMARY KEY (`s_id`, `p_id`),
    CONSTRAINT `fk_requires_skill`
        FOREIGN KEY (`s_id`) REFERENCES `Skill` (`s_id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_requires_project`
        FOREIGN KEY (`p_id`) REFERENCES `Project` (`p_id`)
        ON DELETE CASCADE,
    CONSTRAINT `chk_requires_count` CHECK (`req_count` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- user_has_skill (Users has Skill)
-- =========================================================
CREATE TABLE `user_has_skill` (
    `s_id`      INT         NOT NULL,
    `u_id`      INT         NOT NULL,
    `u_s_level` ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL,
    PRIMARY KEY (`s_id`, `u_id`),
    CONSTRAINT `fk_userhasskill_skill`
        FOREIGN KEY (`s_id`) REFERENCES `Skill` (`s_id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_userhasskill_user`
        FOREIGN KEY (`u_id`) REFERENCES `Users` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Team (Project has Team)
-- =========================================================
CREATE TABLE `Team` (
    `t_id`        INT AUTO_INCREMENT,
    `p_id`        INT          NOT NULL,
    `team_name`   VARCHAR(150) NOT NULL,
    `create_date` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`t_id`),
    CONSTRAINT `fk_team_project`
        FOREIGN KEY (`p_id`) REFERENCES `Project` (`p_id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Joins (Users joins Team)
-- =========================================================
CREATE TABLE `Joins` (
    `u_id` INT          NOT NULL,
    `t_id` INT          NOT NULL,
    `role` ENUM('owner','member') NOT NULL DEFAULT 'member',
    `date` DATE         NOT NULL,
    PRIMARY KEY (`u_id`, `t_id`),
    CONSTRAINT `fk_joins_user`
        FOREIGN KEY (`u_id`) REFERENCES `Users` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_joins_team`
        FOREIGN KEY (`t_id`) REFERENCES `Team` (`t_id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Task (Project contains Task, assigned to a User)
-- parent_task_id enables subtasks -> used for the recursive CTE demo
-- =========================================================
CREATE TABLE `Task` (
    `task_id`        INT AUTO_INCREMENT,
    `p_id`            INT          NOT NULL,
    `u_id`            INT          NULL,
    `parent_task_id`  INT          NULL,
    `t_name`          VARCHAR(150) NOT NULL,
    `status`          ENUM('To Do','In Progress','Done','Blocked') NOT NULL DEFAULT 'To Do',
    `priority`        ENUM('Low','Medium','High','Critical') NOT NULL DEFAULT 'Medium',
    `due_date`        DATE         NULL,
    `description`     TEXT         NULL,
    PRIMARY KEY (`task_id`),
    CONSTRAINT `fk_task_project`
        FOREIGN KEY (`p_id`) REFERENCES `Project` (`p_id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_task_user`
        FOREIGN KEY (`u_id`) REFERENCES `Users` (`id`)
        ON DELETE SET NULL,
    CONSTRAINT `fk_task_parent`
        FOREIGN KEY (`parent_task_id`) REFERENCES `Task` (`task_id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- Application (User submits Application to Project, reviewed by a User)
-- =========================================================
CREATE TABLE `Application` (
    `a_id`          INT AUTO_INCREMENT,
    `applicant_id`  INT         NOT NULL,
    `p_id`          INT         NOT NULL,
    `msg`           TEXT        NULL,
    `status`        ENUM('Pending','Accepted','Rejected') NOT NULL DEFAULT 'Pending',
    `a_date`        DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `decision_date` DATETIME    NULL,
    `reviewer_id`   INT         NULL,
    PRIMARY KEY (`a_id`),
    CONSTRAINT `fk_application_applicant`
        FOREIGN KEY (`applicant_id`) REFERENCES `Users` (`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_application_project`
        FOREIGN KEY (`p_id`) REFERENCES `Project` (`p_id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_application_reviewer`
        FOREIGN KEY (`reviewer_id`) REFERENCES `Users` (`id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- NOTE: no UNIQUE(applicant_id, p_id) here on purpose — a user may be
-- rejected and legitimately re-apply later. "No duplicate PENDING
-- application" is enforced procedurally in sql/procedures.sql
-- (apply_to_project), not as a blunt table constraint.
-- NOTE: MySQL forbids a CHECK constraint on a column that's also part
-- of a FK with an ON DELETE/UPDATE referential action (reviewer_id <>
-- applicant_id would need that here), so "no self-review" is enforced
-- in sql/procedures.sql (decide_application) instead.
