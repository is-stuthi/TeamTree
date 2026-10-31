-- =========================================================
-- TeamTREE schema v2 (MySQL 8.0)
-- Full apply = reset: every table is dropped and recreated.
-- Applied by api/scripts/migrate.py (see db-migrate skill).
-- =========================================================

CREATE DATABASE IF NOT EXISTS teamtree CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE teamtree;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Ownership_Transfer, Application, Task, Joins, Team,
                     user_has_skill, Requires, Domain, Skill, Project, Users;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------
-- USER (one account type; admin/member is the app role)
-- ---------------------------------------------------------
CREATE TABLE Users (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    f_name           VARCHAR(50)  NOT NULL,
    m_name           VARCHAR(50)  NULL,
    l_name           VARCHAR(50)  NOT NULL,
    email            VARCHAR(150) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    role             ENUM('admin','member') NOT NULL DEFAULT 'member',
    bio              TEXT         NULL,
    location         VARCHAR(150) NULL,
    u_photo          VARCHAR(255) NULL,
    dob              DATE         NULL,
    experience_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL DEFAULT 'Beginner',
    availability     ENUM('Full-time','Part-time','Weekends','Unavailable') NOT NULL DEFAULT 'Part-time',
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    CONSTRAINT chk_users_email CHECK (email LIKE '%_@_%._%')
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- PROJECT (USER -CREATES-> PROJECT, 1:N via owner_id)
-- ---------------------------------------------------------
CREATE TABLE Project (
    p_id          INT AUTO_INCREMENT PRIMARY KEY,
    owner_id      INT          NOT NULL,
    p_name        VARCHAR(150) NOT NULL,
    description   TEXT         NULL,
    deadline      DATE         NULL,
    status        ENUM('Open','Ongoing','Completed','Closed') NOT NULL DEFAULT 'Open',
    max_team_size INT          NULL,
    creation_date DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_owner FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_project_deadline CHECK (deadline IS NULL OR deadline >= DATE(creation_date)),
    CONSTRAINT chk_project_capacity CHECK (max_team_size IS NULL OR max_team_size >= 1)
) ENGINE=InnoDB;

-- Multivalued attribute "domain" of PROJECT
CREATE TABLE Domain (
    project_id INT          NOT NULL,
    d_name     VARCHAR(100) NOT NULL,
    PRIMARY KEY (project_id, d_name),
    CONSTRAINT fk_domain_project FOREIGN KEY (project_id) REFERENCES Project(p_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- SKILL (name unique after case/whitespace normalisation)
-- ---------------------------------------------------------
CREATE TABLE Skill (
    s_id        INT AUTO_INCREMENT PRIMARY KEY,
    s_name      VARCHAR(100) NOT NULL,
    s_name_norm VARCHAR(100) AS (LOWER(TRIM(s_name))) STORED,
    category    VARCHAR(100) NULL,
    UNIQUE KEY uq_skill_name_norm (s_name_norm)
) ENGINE=InnoDB;

-- PROJECT -REQUIRES-> SKILL (M:N, relationship attributes level/role/count)
CREATE TABLE Requires (
    p_id      INT          NOT NULL,
    s_id      INT          NOT NULL,
    req_role  VARCHAR(100) NOT NULL DEFAULT 'Contributor',
    p_s_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL,
    req_count INT          NOT NULL DEFAULT 1,
    PRIMARY KEY (p_id, s_id, req_role),
    CONSTRAINT fk_requires_project FOREIGN KEY (p_id) REFERENCES Project(p_id) ON DELETE CASCADE,
    CONSTRAINT fk_requires_skill   FOREIGN KEY (s_id) REFERENCES Skill(s_id)   ON DELETE RESTRICT,
    CONSTRAINT chk_requires_count CHECK (req_count > 0)
) ENGINE=InnoDB;

-- USER -HAS-> SKILL (M:N, relationship attribute proficiency)
CREATE TABLE user_has_skill (
    u_id      INT NOT NULL,
    s_id      INT NOT NULL,
    u_s_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL,
    PRIMARY KEY (u_id, s_id),
    CONSTRAINT fk_uhs_user  FOREIGN KEY (u_id) REFERENCES Users(id)   ON DELETE CASCADE,
    CONSTRAINT fk_uhs_skill FOREIGN KEY (s_id) REFERENCES Skill(s_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- TEAM (PROJECT -HAS-> TEAM, 1:1 enforced by UNIQUE p_id)
-- ---------------------------------------------------------
CREATE TABLE Team (
    t_id        INT AUTO_INCREMENT PRIMARY KEY,
    p_id        INT          NOT NULL,
    team_name   VARCHAR(150) NOT NULL,
    create_date DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_team_project (p_id),
    CONSTRAINT fk_team_project FOREIGN KEY (p_id) REFERENCES Project(p_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- USER -JOINS-> TEAM (M:N with history).
-- active_flag is 1 while active, NULL after leaving, so the UNIQUE index
-- allows many past rows but only one active row per (team, user).
CREATE TABLE Joins (
    j_id        INT AUTO_INCREMENT PRIMARY KEY,
    t_id        INT          NOT NULL,
    u_id        INT          NOT NULL,
    role        VARCHAR(100) NOT NULL DEFAULT 'Member',
    join_date   DATE         NOT NULL,
    leave_date  DATE         NULL,
    active_flag TINYINT AS (IF(leave_date IS NULL, 1, NULL)) STORED,
    UNIQUE KEY uq_joins_active (t_id, u_id, active_flag),
    CONSTRAINT fk_joins_team FOREIGN KEY (t_id) REFERENCES Team(t_id) ON DELETE RESTRICT,
    CONSTRAINT fk_joins_user FOREIGN KEY (u_id) REFERENCES Users(id)  ON DELETE RESTRICT,
    CONSTRAINT chk_joins_dates CHECK (leave_date IS NULL OR leave_date >= join_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- TASK (PROJECT -CONTAINS-> TASK, USER -ASSIGNED_TO-> TASK, subtasks)
-- ---------------------------------------------------------
CREATE TABLE Task (
    task_id        INT AUTO_INCREMENT PRIMARY KEY,
    p_id           INT          NOT NULL,
    u_id           INT          NULL,
    parent_task_id INT          NULL,
    t_name         VARCHAR(150) NOT NULL,
    description    TEXT         NULL,
    status         ENUM('To Do','In Progress','Done','Blocked') NOT NULL DEFAULT 'To Do',
    priority       ENUM('Low','Medium','High','Critical')       NOT NULL DEFAULT 'Medium',
    due_date       DATE         NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_task_project FOREIGN KEY (p_id)           REFERENCES Project(p_id) ON DELETE RESTRICT,
    CONSTRAINT fk_task_user    FOREIGN KEY (u_id)           REFERENCES Users(id)     ON DELETE SET NULL,
    CONSTRAINT fk_task_parent  FOREIGN KEY (parent_task_id) REFERENCES Task(task_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- APPLICATION (USER -SUBMITS-> APPLICATION -FOR-> PROJECT).
-- The reviewer is derived: Project.owner_id. pending_flag allows
-- only one Pending application per (applicant, project).
-- ---------------------------------------------------------
CREATE TABLE Application (
    a_id          INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id  INT      NOT NULL,
    p_id          INT      NOT NULL,
    msg           TEXT     NULL,
    status        ENUM('Pending','Accepted','Rejected','Withdrawn') NOT NULL DEFAULT 'Pending',
    a_date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decision_date DATETIME NULL,
    pending_flag  TINYINT AS (IF(status = 'Pending', 1, NULL)) STORED,
    UNIQUE KEY uq_application_pending (applicant_id, p_id, pending_flag),
    CONSTRAINT fk_application_applicant FOREIGN KEY (applicant_id) REFERENCES Users(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_application_project   FOREIGN KEY (p_id)         REFERENCES Project(p_id) ON DELETE RESTRICT,
    CONSTRAINT chk_application_decision CHECK (
        (status IN ('Pending','Withdrawn') AND decision_date IS NULL) OR
        (status IN ('Accepted','Rejected') AND decision_date IS NOT NULL))
) ENGINE=InnoDB;

-- Audit trail for ownership transfers (design doc 13.10, 16.4)
CREATE TABLE Ownership_Transfer (
    ot_id          INT AUTO_INCREMENT PRIMARY KEY,
    p_id           INT      NOT NULL,
    from_user      INT      NOT NULL,
    to_user        INT      NOT NULL,
    transferred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ot_project FOREIGN KEY (p_id)      REFERENCES Project(p_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ot_from    FOREIGN KEY (from_user) REFERENCES Users(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_ot_to      FOREIGN KEY (to_user)   REFERENCES Users(id)     ON DELETE RESTRICT,
    CONSTRAINT chk_ot_distinct CHECK (from_user <> to_user)
) ENGINE=InnoDB;
