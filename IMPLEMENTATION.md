# TeamTREE — Implementation Plan

> Companion to [docs/TeamTREE_Design_Document.md](docs/TeamTREE_Design_Document.md).
> The design doc says **what** and **why**. This file says **how**, in what order, and with which tooling.

**Stack:** MySQL 8 · FastAPI (Python 3.12, raw SQL, no ORM) · Vite + React 18 + TypeScript · shadcn/ui · Docker Compose

---

## 0. Working rules (apply to every phase)

| Rule | What it means in practice |
|---|---|
| **Skills first** | Repetitive workflows live in `.claude/skills/*` and load on demand. `CLAUDE.md` only points to them. Before doing a workflow by hand, check whether a skill covers it. |
| **Model routing** | Use the subagents in `.claude/agents/`: `sql-scout` (Haiku), `builder` (Sonnet), `architect` (Opus). See §7. |
| **shadcn only** | UI primitives come from `npx shadcn@latest add <name>` into `web/src/components/ui/`. Don't hand-roll buttons, inputs, tables or dialogs. |
| **Schema-driven UI** | Forms and dashboards are **JSON specs** in `web/src/specs/`, rendered by static components (`SchemaForm`, `SchemaDashboard`). Adding a form means writing JSON, not JSX. |
| **Atomic components** | Every custom `.tsx`/`.ts` file stays at ≤ 150 lines (ESLint `max-lines` enforces this). If a file grows past that, split it. |
| **Generators for boilerplate** | Use the shadcn CLI, `openapi-typescript`, `json-schema-to-typescript` and `plop` (router, component, page). Don't type boilerplate by hand. |
| **TS defs over source** | To learn the API contract, read `web/src/api/schema.d.ts` and `web/src/api/ui-schemas.d.ts`, not `api/app/**`. Regenerate them with the `gen-types` skill. |

---

## 1. Repository layout

```
TeamTree/
├── CLAUDE.md                     # short: rules + pointers to skills/agents
├── IMPLEMENTATION.md             # this file
├── docker-compose.yml            # mysql:8.0 (+ api)
├── .claude/
│   ├── agents/                   # sql-scout (haiku), builder (sonnet), architect (opus)
│   └── skills/                   # db-migrate, gen-types, scaffold, schema-form, check-docker, rule-tests
├── docs/                         # design doc, ER diagram
├── raw/schema.sql                # v1 (kept for history; superseded by db/)
├── db/
│   ├── 001_schema.sql            # tables (schema v2, §2)
│   ├── 002_triggers.sql
│   ├── 003_procedures.sql
│   ├── 004_views.sql
│   ├── 005_indexes.sql
│   └── seed.sql
├── api/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py               # FastAPI app, router registration, error mapping
│   │   ├── db.py                 # aiomysql pool, call_proc(), fetch_view()
│   │   ├── auth.py               # bcrypt + JWT
│   │   ├── errors.py             # SIGNAL message → HTTP status map
│   │   ├── models/               # Pydantic request/response models (source of truth)
│   │   ├── routers/              # auth users skills projects applications teams tasks matching analytics ui_schemas
│   │   ├── services/matching.py  # transparent weighted scoring (§3.3)
│   │   └── ui_schemas/           # form + dashboard JSON specs exported to the frontend
│   ├── scripts/dump_openapi.py
│   └── tests/                    # pytest business-rule suite (§8)
├── web/
│   ├── components.json           # shadcn config
│   ├── plopfile.js
│   ├── plop-templates/
│   └── src/
│       ├── api/schema.d.ts       # GENERATED, do not edit
│       ├── api/ui-schemas.d.ts   # GENERATED, do not edit
│       ├── api/client.ts         # openapi-fetch instance (≈10 lines)
│       ├── components/ui/        # shadcn (generated, exempt from LOC rule)
│       ├── components/schema/    # SchemaForm, SchemaDashboard, field/*, widget/*
│       ├── components/app/       # small app-specific components
│       ├── pages/
│       └── specs/                # forms/*.json, dashboards/*.json
```

---

## 2. Database — schema v2

v2 replaces `raw/schema.sql`. Changes from v1, and why:

| Area | v1 | v2 | Design-doc reason |
|---|---|---|---|
| `Users.password` | plaintext name | `password_hash` | §12.1 rule 3 |
| `Users` | no deactivation | `is_active`, `experience_level`, `availability` ENUM | §6.1, §10, §13.13 |
| `Project.status` | Planning/Active/Completed/Cancelled | **Open/Ongoing/Completed/Closed** | §6.3, rule 16 |
| `Project` | no capacity | `max_team_size` (includes owner) | §13.3 |
| `Project` | no date check | `CHECK deadline >= creation date` | rule 15 |
| FKs to `Users`/`Project` | `ON DELETE CASCADE` | `RESTRICT` (soft delete) | §13.12, §13.13 |
| `Skill` | case-sensitive unique | generated `s_name_norm` UNIQUE, `category` | rule 8 |
| `Requires` PK | (s_id, p_id) | (p_id, s_id, req_role) | §14.1: same skill for several roles |
| `Team.p_id` | not unique | `UNIQUE` | 1:1, rule 13 |
| `Joins` | composite PK, no history | surrogate `j_id`, `leave_date`, one **active** row per (team, user) | §13.8, rule 27 |
| `Joins.role` | owner/member ENUM | free-text role (e.g., "Backend Dev", "Owner") | §7.8 |
| `Application.status` | no Withdrawn | adds **Withdrawn** | §6.4 |
| `Application.reviewer_id` | stored | **dropped**, derived via `Project.owner_id` | §7.6, §14.2 |
| `Application` | no duplicate guard | one **Pending** row per (user, project) | rule 20 |
| new | — | `Ownership_Transfer` audit table | §13.10, §16.4 |

**Policies decided (design doc §22):**
- The owner is **automatically a team member** with role `Owner`, and counts toward `max_team_size`.
- **Reapplication** is allowed after Rejected or Withdrawn. Only one *Pending* application per pair is allowed.
- **Membership history** is preserved: leaving sets `leave_date` and never deletes the row.
- **Skill catalogue** is admin-managed (`Users.is_admin`). Users pick from the catalogue.
- **Project status meanings:**
  - `Open`: recruiting; accepts applications.
  - `Ongoing`: work started; no new applications, but pending ones can still be decided.
  - `Completed`: delivered.
  - `Closed`: abandoned or archived (soft delete).
  - *Overdue* is **derived** as `deadline < CURDATE() AND status IN ('Open','Ongoing')`. It is not stored.

The "one active row" rule uses generated `*_flag` columns: the flag is `1` while the row is active and `NULL` otherwise. A `UNIQUE` index that includes the flag therefore allows many inactive (NULL) rows but only one active row.

### 2.1 `db/001_schema.sql`

```sql
CREATE DATABASE IF NOT EXISTS teamtree CHARACTER SET utf8mb4;
USE teamtree;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Ownership_Transfer, Application, Task, Joins, Team,
                     user_has_skill, Requires, Domain, Skill, Project, Users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE Users (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    f_name           VARCHAR(50)  NOT NULL,
    m_name           VARCHAR(50)  NULL,
    l_name           VARCHAR(50)  NOT NULL,
    email            VARCHAR(150) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    bio              TEXT         NULL,
    location         VARCHAR(150) NULL,
    u_photo          VARCHAR(255) NULL,
    dob              DATE         NULL,                     -- age is derived, never stored
    experience_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL DEFAULT 'Beginner',
    availability     ENUM('Full-time','Part-time','Weekends','Unavailable') NOT NULL DEFAULT 'Part-time',
    is_admin         BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE Project (
    p_id          INT AUTO_INCREMENT PRIMARY KEY,
    owner_id      INT          NOT NULL,
    p_name        VARCHAR(150) NOT NULL,
    description   TEXT         NULL,
    deadline      DATE         NULL,
    status        ENUM('Open','Ongoing','Completed','Closed') NOT NULL DEFAULT 'Open',
    max_team_size INT          NULL,                        -- NULL = uncapped; includes owner
    creation_date DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_owner FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_project_deadline CHECK (deadline IS NULL OR deadline >= DATE(creation_date)),
    CONSTRAINT chk_project_capacity CHECK (max_team_size IS NULL OR max_team_size >= 1)
) ENGINE=InnoDB;

CREATE TABLE Domain (                                       -- multivalued attribute of Project
    project_id INT          NOT NULL,
    d_name     VARCHAR(100) NOT NULL,
    PRIMARY KEY (project_id, d_name),
    CONSTRAINT fk_domain_project FOREIGN KEY (project_id) REFERENCES Project(p_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Skill (
    s_id        INT AUTO_INCREMENT PRIMARY KEY,
    s_name      VARCHAR(100) NOT NULL,
    s_name_norm VARCHAR(100) AS (LOWER(TRIM(s_name))) STORED,
    category    VARCHAR(100) NULL,
    UNIQUE KEY uq_skill_name_norm (s_name_norm)
) ENGINE=InnoDB;

CREATE TABLE Requires (                                     -- PROJECT —REQUIRES— SKILL
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

CREATE TABLE user_has_skill (                               -- USER —HAS— SKILL
    u_id      INT NOT NULL,
    s_id      INT NOT NULL,
    u_s_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL,
    PRIMARY KEY (u_id, s_id),
    CONSTRAINT fk_uhs_user  FOREIGN KEY (u_id) REFERENCES Users(id) ON DELETE CASCADE,
    CONSTRAINT fk_uhs_skill FOREIGN KEY (s_id) REFERENCES Skill(s_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Team (                                         -- PROJECT —HAS— TEAM (1:1)
    t_id        INT AUTO_INCREMENT PRIMARY KEY,
    p_id        INT          NOT NULL,
    team_name   VARCHAR(150) NOT NULL,
    create_date DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_team_project (p_id),
    CONSTRAINT fk_team_project FOREIGN KEY (p_id) REFERENCES Project(p_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Joins (                                        -- USER —JOINS— TEAM, with history
    j_id        INT AUTO_INCREMENT PRIMARY KEY,
    t_id        INT          NOT NULL,
    u_id        INT          NOT NULL,
    role        VARCHAR(100) NOT NULL DEFAULT 'Member',
    join_date   DATE         NOT NULL,
    leave_date  DATE         NULL,
    active_flag TINYINT AS (IF(leave_date IS NULL, 1, NULL)) STORED,
    UNIQUE KEY uq_joins_active (t_id, u_id, active_flag),
    CONSTRAINT fk_joins_team FOREIGN KEY (t_id) REFERENCES Team(t_id)  ON DELETE RESTRICT,
    CONSTRAINT fk_joins_user FOREIGN KEY (u_id) REFERENCES Users(id)   ON DELETE RESTRICT,
    CONSTRAINT chk_joins_dates CHECK (leave_date IS NULL OR leave_date >= join_date)
) ENGINE=InnoDB;

CREATE TABLE Task (                                         -- PROJECT —CONTAINS— TASK, USER —ASSIGNED— TASK
    task_id        INT AUTO_INCREMENT PRIMARY KEY,
    p_id           INT          NOT NULL,
    u_id           INT          NULL,                       -- NULL = unassigned
    parent_task_id INT          NULL,                       -- subtasks (recursive CTE demo)
    t_name         VARCHAR(150) NOT NULL,
    description    TEXT         NULL,
    status         ENUM('To Do','In Progress','Done','Blocked') NOT NULL DEFAULT 'To Do',
    priority       ENUM('Low','Medium','High','Critical')       NOT NULL DEFAULT 'Medium',
    due_date       DATE         NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_task_project FOREIGN KEY (p_id)           REFERENCES Project(p_id)  ON DELETE RESTRICT,
    CONSTRAINT fk_task_user    FOREIGN KEY (u_id)           REFERENCES Users(id)      ON DELETE SET NULL,
    CONSTRAINT fk_task_parent  FOREIGN KEY (parent_task_id) REFERENCES Task(task_id)  ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Application (                                  -- USER —SUBMITS— APPLICATION —FOR— PROJECT
    a_id          INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id  INT      NOT NULL,
    p_id          INT      NOT NULL,
    msg           TEXT     NULL,
    status        ENUM('Pending','Accepted','Rejected','Withdrawn') NOT NULL DEFAULT 'Pending',
    a_date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decision_date DATETIME NULL,                            -- REVIEWS relationship attribute
    pending_flag  TINYINT AS (IF(status = 'Pending', 1, NULL)) STORED,
    UNIQUE KEY uq_application_pending (applicant_id, p_id, pending_flag),
    CONSTRAINT fk_application_applicant FOREIGN KEY (applicant_id) REFERENCES Users(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_application_project   FOREIGN KEY (p_id)         REFERENCES Project(p_id) ON DELETE RESTRICT,
    CONSTRAINT chk_application_decision CHECK (
        (status IN ('Pending','Withdrawn') AND decision_date IS NULL) OR
        (status IN ('Accepted','Rejected') AND decision_date IS NOT NULL))
) ENGINE=InnoDB;
-- Reviewer = Project.owner_id (derived). No reviewer_id column.

CREATE TABLE Ownership_Transfer (
    ot_id          INT AUTO_INCREMENT PRIMARY KEY,
    p_id           INT      NOT NULL,
    from_user      INT      NOT NULL,
    to_user        INT      NOT NULL,
    transferred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ot_project FOREIGN KEY (p_id)      REFERENCES Project(p_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ot_from    FOREIGN KEY (from_user) REFERENCES Users(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_ot_to      FOREIGN KEY (to_user)   REFERENCES Users(id)     ON DELETE RESTRICT
) ENGINE=InnoDB;
```

> The rule "only Pending/Withdrawn may lack a decision date" lives in a CHECK. MySQL 8.0.16+ enforces CHECKs.

### 2.2 `db/002_triggers.sql`

Triggers are kept to **validation only**. They never silently write other rows (design doc §17.2).

```sql
DELIMITER $$

CREATE TRIGGER trg_application_bi BEFORE INSERT ON Application
FOR EACH ROW
BEGIN
    DECLARE v_owner INT; DECLARE v_status VARCHAR(10); DECLARE v_cap INT; DECLARE v_members INT;

    SELECT owner_id, status, max_team_size INTO v_owner, v_status, v_cap
      FROM Project WHERE p_id = NEW.p_id;

    IF v_status <> 'Open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_OPEN';
    END IF;
    IF v_owner = NEW.applicant_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'SELF_APPLICATION';
    END IF;
    IF v_cap IS NOT NULL THEN
        SELECT COUNT(*) INTO v_members
          FROM Joins j JOIN Team t ON t.t_id = j.t_id
         WHERE t.p_id = NEW.p_id AND j.leave_date IS NULL;
        IF v_members >= v_cap THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_FULL';
        END IF;
    END IF;
END$$

-- Same body for BEFORE INSERT and BEFORE UPDATE, shared through a procedure.
CREATE PROCEDURE validate_task(IN p_pid INT, IN p_uid INT, IN p_due DATE)
BEGIN
    DECLARE v_deadline DATE;
    IF p_uid IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM Joins j JOIN Team t ON t.t_id = j.t_id
         WHERE t.p_id = p_pid AND j.u_id = p_uid AND j.leave_date IS NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ASSIGNEE_NOT_MEMBER';
    END IF;
    SELECT deadline INTO v_deadline FROM Project WHERE p_id = p_pid;
    IF p_due IS NOT NULL AND v_deadline IS NOT NULL AND p_due > v_deadline THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TASK_AFTER_DEADLINE';
    END IF;
END$$

CREATE TRIGGER trg_task_bi BEFORE INSERT ON Task
FOR EACH ROW CALL validate_task(NEW.p_id, NEW.u_id, NEW.due_date)$$

CREATE TRIGGER trg_task_bu BEFORE UPDATE ON Task
FOR EACH ROW CALL validate_task(NEW.p_id, NEW.u_id, NEW.due_date)$$

DELIMITER ;
```

### 2.3 `db/003_procedures.sql`

All multi-step workflows run as transactional procedures. Every procedure follows this pattern:

```sql
DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
START TRANSACTION;  ...validate with SIGNAL...  ...writes...  COMMIT;
```

| Procedure | Signature | Steps |
|---|---|---|
| `create_project` | `(owner, name, desc, deadline, max_size, OUT p_id)` | Insert Project → insert Team (`<name> Team`) → insert owner into Joins (role `Owner`). |
| `apply_to_project` | `(user, p_id, msg, OUT a_id)` | Insert Application. The trigger and the pending-unique index do the validation. A duplicate maps `ER_DUP_ENTRY` → `DUPLICATE_PENDING`. |
| `decide_application` | `(a_id, actor, decision, role)` | See below. |
| `withdraw_application` | `(a_id, actor)` | Actor must be the applicant, and status must be Pending → `Withdrawn`. |
| `assign_task` | `(task_id, actor, assignee)` | Actor must be the owner or an active member; the trigger checks the assignee. |
| `remove_member` | `(p_id, actor, user)` | Actor must be the owner and the user cannot be the owner. Set `leave_date = CURDATE()`, then `UPDATE Task SET u_id = NULL WHERE p_id=… AND u_id=… AND status <> 'Done'`. |
| `leave_team` | `(p_id, user)` | Same as `remove_member`, self-initiated. The owner must transfer ownership first. |
| `transfer_ownership` | `(p_id, actor, new_owner)` | Actor must be the current owner and `new_owner` must be an active member. Update `owner_id`, swap the `Owner`/`Member` roles in Joins, and insert into `Ownership_Transfer`. |

`decide_application` is the core transaction for design doc §16.1:

```sql
DELIMITER $$
CREATE PROCEDURE decide_application(IN p_a_id INT, IN p_actor INT,
                                    IN p_decision VARCHAR(10), IN p_role VARCHAR(100))
BEGIN
    DECLARE v_pid, v_applicant, v_owner, v_cap, v_tid, v_members INT;
    DECLARE v_status, v_pstatus VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

    IF p_decision NOT IN ('Accepted','Rejected') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'BAD_DECISION';
    END IF;

    START TRANSACTION;
    SELECT p_id, applicant_id, status INTO v_pid, v_applicant, v_status
      FROM Application WHERE a_id = p_a_id FOR UPDATE;
    IF v_pid IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_FOUND'; END IF;

    -- Lock the project row: serialises concurrent accepts for the capacity check.
    SELECT owner_id, status, max_team_size INTO v_owner, v_pstatus, v_cap
      FROM Project WHERE p_id = v_pid FOR UPDATE;
    IF v_owner <> p_actor   THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'NOT_OWNER';       END IF;
    IF v_status <> 'Pending' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_PENDING'; END IF;

    IF p_decision = 'Accepted' THEN
        IF v_pstatus NOT IN ('Open','Ongoing') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_NOT_ACCEPTING';
        END IF;
        SELECT t_id INTO v_tid FROM Team WHERE p_id = v_pid;
        SELECT COUNT(*) INTO v_members FROM Joins WHERE t_id = v_tid AND leave_date IS NULL;
        IF v_cap IS NOT NULL AND v_members >= v_cap THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_FULL';
        END IF;
        INSERT INTO Joins (t_id, u_id, role, join_date)
        VALUES (v_tid, v_applicant, COALESCE(p_role, 'Member'), CURDATE());
    END IF;

    UPDATE Application SET status = p_decision, decision_date = NOW() WHERE a_id = p_a_id;
    COMMIT;
END$$
DELIMITER ;
```

If the `Joins` insert fails (for example, an active duplicate), the exit handler rolls back the status change too. This covers design doc §13.7.

### 2.4 `db/004_views.sql`

Proficiency is compared by ENUM ordinal (`level + 0`: Beginner = 1 … Expert = 4).

| View | Purpose / key columns |
|---|---|
| `OpenProjects` | Open projects + owner name + domains (`GROUP_CONCAT`) + required skills + `is_overdue` |
| `ProjectApplicationSummary` | p_id, counts per status, `acceptance_rate = accepted / NULLIF(accepted + rejected, 0)` (excludes Pending and Withdrawn, per §11.5) |
| `UserSkillProfiles` | user, skill, category, level |
| `ProjectSkillRequirements` | project, skill, role, level, count |
| `TeamMemberDetails` | active and historical members with role, join_date, leave_date |
| `TaskProgressSummary` | p_id, total, per-status counts, % done, overdue tasks |
| `TopInDemandSkills` | skill, projects_requiring, users_possessing, `demand_supply_ratio` |
| `SkillGap` | requirement vs. active members meeting the level (below) |

```sql
CREATE OR REPLACE VIEW SkillGap AS
SELECT r.p_id, r.s_id, s.s_name, r.req_role, r.p_s_level AS required_level, r.req_count,
       COUNT(DISTINCT uhs.u_id)                                                    AS members_with_skill,
       COUNT(DISTINCT CASE WHEN uhs.u_s_level + 0 >= r.p_s_level + 0 THEN uhs.u_id END) AS qualified_members,
       GREATEST(r.req_count -
                COUNT(DISTINCT CASE WHEN uhs.u_s_level + 0 >= r.p_s_level + 0 THEN uhs.u_id END), 0) AS shortfall
FROM Requires r
JOIN Skill s            ON s.s_id = r.s_id
LEFT JOIN Team t        ON t.p_id = r.p_id
LEFT JOIN Joins j       ON j.t_id = t.t_id AND j.leave_date IS NULL
LEFT JOIN user_has_skill uhs ON uhs.u_id = j.u_id AND uhs.s_id = r.s_id
GROUP BY r.p_id, r.s_id, s.s_name, r.req_role, r.p_s_level, r.req_count;

CREATE OR REPLACE VIEW TopInDemandSkills AS
SELECT s.s_id, s.s_name, s.category,
       (SELECT COUNT(DISTINCT p_id) FROM Requires r WHERE r.s_id = s.s_id)       AS projects_requiring,
       (SELECT COUNT(*)            FROM user_has_skill u WHERE u.s_id = s.s_id) AS users_possessing,
       (SELECT COUNT(DISTINCT p_id) FROM Requires r WHERE r.s_id = s.s_id) /
       NULLIF((SELECT COUNT(*) FROM user_has_skill u WHERE u.s_id = s.s_id), 0) AS demand_supply_ratio
FROM Skill s;
```

A **recursive CTE demo** (the subtask tree) is exposed as `GET /projects/{id}/tasks/tree`:

```sql
WITH RECURSIVE tree AS (
  SELECT task_id, parent_task_id, t_name, 0 AS depth FROM Task WHERE p_id = ? AND parent_task_id IS NULL
  UNION ALL
  SELECT t.task_id, t.parent_task_id, t.t_name, tree.depth + 1
  FROM Task t JOIN tree ON t.parent_task_id = tree.task_id
) SELECT * FROM tree;
```

### 2.5 `db/005_indexes.sql`

```sql
CREATE INDEX ix_users_name        ON Users (l_name, f_name);
CREATE INDEX ix_project_status    ON Project (status, deadline);
CREATE INDEX ix_project_owner     ON Project (owner_id);
CREATE INDEX ix_domain_name       ON Domain (d_name);
CREATE INDEX ix_requires_skill    ON Requires (s_id, p_s_level);
CREATE INDEX ix_uhs_skill         ON user_has_skill (s_id, u_s_level);
CREATE INDEX ix_application_proj  ON Application (p_id, status);
CREATE INDEX ix_task_project      ON Task (p_id, status);
CREATE INDEX ix_task_user         ON Task (u_id, status);
CREATE INDEX ix_joins_user        ON Joins (u_id, leave_date);
```

`Users.email`, `Skill.s_name_norm` and `Team.p_id` are already indexed by their UNIQUE keys.

### 2.6 `db/seed.sql`
Seed about 12 users (1 admin), 25 skills in 5 categories, 8 projects across all four statuses, and applications in every status. Include at least one project with a deliberate skill gap and one at capacity, so every analytic and test has data. Seed generation goes to **`sql-scout` (Haiku)**.

---

## 3. Backend (FastAPI)

### 3.1 Conventions
- `db.py` exposes `call_proc(name, *args) -> dict` (returns OUT params), `fetch_all(sql, params)` and `fetch_view(name, where)`. No ORM: routers read SQL, which keeps the DBMS logic visible.
- `errors.py` maps the `SIGNAL` messages to HTTP statuses in one place:

| Message | HTTP |
|---|---|
| `NOT_OWNER` | 403 |
| `APP_NOT_FOUND` | 404 |
| `PROJECT_NOT_OPEN`, `PROJECT_FULL`, `APP_NOT_PENDING`, `ASSIGNEE_NOT_MEMBER`, `TASK_AFTER_DEADLINE`, `PROJECT_NOT_ACCEPTING` | 409 |
| `SELF_APPLICATION`, `BAD_DECISION` | 422 |
| `ER_DUP_ENTRY` on `uq_application_pending` | 409 `DUPLICATE_PENDING` |
| `ER_DUP_ENTRY` on `uq_users_email` | 409 `EMAIL_TAKEN` |
| `ER_CHECK_CONSTRAINT_VIOLATED` | 422 |

- Auth: `passlib[bcrypt]` + `python-jose` JWT. A `current_user` dependency is used everywhere. Deactivated users can't log in.
- Each router file stays ≤ 150 lines, the same rule as the frontend. Scaffold routers with `plop router <name>` (see the `scaffold` skill).

### 3.2 Endpoints

| Router | Endpoints |
|---|---|
| `auth` | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| `users` | `GET/PATCH /users/me`, `GET /users/{id}`, `PUT/DELETE /users/me/skills/{s_id}`, `POST /users/me/deactivate` |
| `skills` | `GET /skills?q=&category=`, `POST/PATCH /skills` (admin) |
| `projects` | `GET /projects?status=&domain=&skill=&deadline_before=`, `POST /projects` (→ `create_project`), `GET/PATCH /projects/{id}`, `PUT/DELETE /projects/{id}/requirements`, `POST /projects/{id}/transfer` |
| `applications` | `POST /projects/{id}/applications`, `GET /projects/{id}/applications` (owner), `GET /users/me/applications`, `POST /applications/{id}/decision`, `POST /applications/{id}/withdraw` |
| `teams` | `GET /projects/{id}/team`, `DELETE /projects/{id}/team/{user_id}`, `POST /projects/{id}/team/leave`, `GET /users/me/teams` |
| `tasks` | `GET/POST /projects/{id}/tasks`, `GET /projects/{id}/tasks/tree`, `PATCH /tasks/{id}`, `POST /tasks/{id}/assign`, `GET /users/me/tasks` |
| `matching` | `GET /projects/{id}/candidates`, `GET /users/me/recommended-projects`, `GET /projects/{id}/skill-gap` |
| `analytics` | `GET /analytics/{skills,projects,users,teams,applications}` (views only) |
| `ui_schemas` | `GET /ui-schemas`, `GET /ui-schemas/{name}` |

### 3.3 Matching (`services/matching.py`)
1. SQL fetches, for one project, every active user's level for each required skill (`LEFT JOIN user_has_skill`).
2. Python scores each candidate with the transparent weights from design doc §10:

| Factor | Weight | Computation |
|---|---|---|
| Coverage | 50 | share of required skills the user has at all |
| Proficiency | 20 | mean of `min(user_level / required_level, 1)` over covered skills |
| Experience | 15 | `experience_level` ordinal / 4 |
| Domain | 10 | 1 if the user has worked on a project with an overlapping `Domain`, else 0 |
| Availability | 5 | Full-time 1, Part-time 0.6, Weekends 0.3, Unavailable 0 |

3. The result is `{user, score, breakdown: {factor: points}, missing_skills: [...]}`. The UI shows the breakdown and labels the score as "indicative" (per §10, don't present it as objective).
4. Recommended projects use the same scorer in reverse (one user × all Open projects).

### 3.4 UI schemas (schema-driven UI source)
`ui_schemas/` holds one Python module per spec. Each module returns `Model.model_json_schema()` plus a `ui` block:

```json
{
  "name": "project_create",
  "title": "Create project",
  "submit": { "method": "POST", "path": "/projects" },
  "schema": { "$ref": "#/components/schemas/ProjectCreate" },
  "ui": {
    "order": ["p_name", "description", "domains", "deadline", "max_team_size"],
    "fields": {
      "description":   { "widget": "textarea", "rows": 5 },
      "domains":       { "widget": "tags" },
      "deadline":      { "widget": "date" },
      "max_team_size": { "widget": "number", "help": "Includes you (the owner)" }
    }
  }
}
```

Because Pydantic models generate both the OpenAPI spec and the UI specs, validation rules exist in only one place.

---

## 4. Frontend (Vite + React + shadcn)

### 4.1 Setup (all generated)
```bash
npm create vite@latest web -- --template react-ts
cd web && npx shadcn@latest init
npx shadcn@latest add button card input textarea select checkbox badge table tabs dialog \
    form label sonner calendar popover chart skeleton separator dropdown-menu avatar progress
npm i react-router-dom @tanstack/react-query openapi-fetch react-hook-form zod @hookform/resolvers
npm i -D openapi-typescript json-schema-to-typescript plop vitest @testing-library/react
```

ESLint (`eslint.config.js`):
```js
{ files: ["src/**/*.{ts,tsx}"], ignores: ["src/components/ui/**", "src/api/*.d.ts"],
  rules: { "max-lines": ["error", { max: 150, skipBlankLines: true, skipComments: true }] } }
```

### 4.2 Schema renderers (static, ≤ 150 LOC each)

```
components/schema/
  SchemaForm.tsx         # loads spec, builds zod from JSON Schema, renders fields in ui.order
  buildZod.ts            # JSON Schema → zod (string/number/enum/date/array, min/max/required)
  FieldRenderer.tsx      # widget switch → field/*
  field/TextField.tsx  TextareaField.tsx  NumberField.tsx  SelectField.tsx
  field/DateField.tsx  TagsField.tsx      SkillLevelField.tsx (skill + level picker)
  SchemaDashboard.tsx    # loads dashboard spec, lays out widgets in a CSS grid
  WidgetRenderer.tsx     # widget switch → widget/*
  widget/StatWidget.tsx  BarWidget.tsx  PieWidget.tsx  TableWidget.tsx  ProgressWidget.tsx
  useSpec.ts             # react-query hook: GET /ui-schemas/{name} or local specs/*.json
```

**Widget → shadcn mapping:**

| `ui.widget` / JSON type | Component |
|---|---|
| `string` | `Input` |
| `textarea` | `Textarea` |
| `number` / `integer` | `Input type=number` |
| `enum` | `Select` |
| `date` | `Popover` + `Calendar` |
| `boolean` | `Checkbox` |
| `tags` | `Input` + `Badge` list |
| `skill-level` | `Select` (skill) + `Select` (level) rows |

**Dashboard spec** (`specs/dashboards/analytics.json`):
```json
{
  "title": "Platform analytics",
  "grid": { "cols": 3 },
  "widgets": [
    { "type": "stat",  "title": "Open projects", "source": "/analytics/projects", "path": "by_status.Open" },
    { "type": "stat",  "title": "Acceptance rate", "source": "/analytics/applications", "path": "acceptance_rate", "format": "percent" },
    { "type": "bar",   "title": "Skill demand vs supply", "source": "/analytics/skills", "x": "s_name",
      "series": ["projects_requiring", "users_possessing"], "span": 2 },
    { "type": "pie",   "title": "Projects by status", "source": "/analytics/projects", "path": "by_status" },
    { "type": "table", "title": "Skill gaps", "source": "/projects/{id}/skill-gap",
      "columns": ["s_name", "required_level", "req_count", "qualified_members", "shortfall"] }
  ]
}
```

Charts use shadcn `chart` (Recharts) and follow the **dataviz** skill for colours and legends.

### 4.3 Pages (each a thin composition of specs and small components)

| Page | Composition |
|---|---|
| Landing, Login, Register | `SchemaForm` (`login`, `register`) |
| Browse projects | filter `SchemaForm` (`project_filter`) + `ProjectCard` grid |
| Project detail | header, requirements `Table`, Apply `Dialog` → `SchemaForm` (`application_create`) |
| Dashboard | `Tabs`: Profile (`profile_edit`), Skills (`skill-level`), My projects, My applications, My teams, My tasks |
| Owner view | `Tabs`: Requirements, Applications (accept/reject buttons), Team, Tasks, Candidates (match breakdown), Skill gap (`SchemaDashboard`) |
| Analytics | `SchemaDashboard` (`analytics`) |

Scaffold pages with `plop page <Name>` and app components with `plop component <Name>`.

### 4.4 API access
```ts
// src/api/client.ts
import createClient from "openapi-fetch";
import type { paths } from "./schema";
export const api = createClient<paths>({ baseUrl: import.meta.env.VITE_API_URL });
```
All calls are typed from `schema.d.ts`, so there are no hand-written fetch wrappers.

---

## 5. Code generation and TypeScript definitions

| Generator | Input | Output | Command |
|---|---|---|---|
| FastAPI | Pydantic models | `api/openapi.json` | `python api/scripts/dump_openapi.py` |
| openapi-typescript | `openapi.json` | `web/src/api/schema.d.ts` | `npx openapi-typescript ../api/openapi.json -o src/api/schema.d.ts` |
| json-schema-to-typescript | `/ui-schemas/*` | `web/src/api/ui-schemas.d.ts` | `npx json2ts -i ../api/ui_schemas_out -o src/api/ui-schemas.d.ts` |
| shadcn CLI | — | `components/ui/*` | `npx shadcn@latest add <x>` |
| plop | templates | routers, components, pages | `npx plop router\|component\|page` |

`web/package.json` → `"gen": "npm run gen:openapi && npm run gen:ui"`. CI and the `gen-types` skill run `git diff --exit-code src/api/` to catch stale types.

**Rule for Claude:** read the API contract from the `.d.ts` files, which are compact and authoritative. Open `api/app/**` only when you are changing backend behaviour.

---

## 6. Skills and progressive disclosure

`CLAUDE.md` stays at about 40 lines. Workflows load only when they're needed:

| Skill | When it loads | Typical agent |
|---|---|---|
| `db-migrate` | schema/procedure/view changes, DB reset, seeding | sql-scout / builder |
| `gen-types` | after any Pydantic model or UI-schema change | builder |
| `scaffold` | new router, component or page; adding shadcn components; splitting a file over 150 LOC | builder |
| `schema-form` | new or changed form or dashboard (JSON only) | builder / sql-scout |
| `check-docker` | containers won't start, DB connection errors, port clashes | sql-scout |
| `rule-tests` | running and interpreting the business-rule test suite | sql-scout (summary) / builder (fix) |

Built-in skills to use: `dataviz` (analytics charts), `code-review` / `simplify` (before merging each phase), `run` (launch the app to verify).

---

## 7. Model routing

| Task | Agent | Model |
|---|---|---|
| "What does view X return?", log or test-output summaries, basic DDL, seed data, simple SELECTs, JSON specs for straightforward forms | `sql-scout` | **Haiku** |
| Implementing endpoints, pages and components, routine edits, running generators, standard debugging, writing tests | `builder` | **Sonnet** |
| Schema v2 changes that touch keys or constraints, transaction and locking design, concurrency bugs (double-accept races, deadlocks), cross-cutting refactors, Docker networking problems that resist the `check-docker` skill | `architect` | **Opus** |

**Escalation:** if Haiku gives an uncertain or wrong result, re-run on Sonnet. If Sonnet fails twice on the same bug, or the fix needs schema or transaction redesign, send it to Opus for a **plan only**, then hand back to Sonnet to implement. Opus doesn't write routine code.

---

## 8. Phased build order

Each phase ends with `rule-tests` green for its scope, `npm run lint` passing (LOC cap) and a `code-review` pass.

| Phase | Scope | Skills | Agent | Done when |
|---|---|---|---|---|
| **P0** | `docker-compose.yml`, `db/001–005`, `seed.sql`, `api` skeleton + `/health` | db-migrate, check-docker | architect (review DDL) → builder | `docker compose up` loads all SQL without errors; seed rows present |
| **P1** | auth, users, skills; shadcn init; `SchemaForm` + login/register/profile specs | scaffold, gen-types, schema-form | builder | register → login → add skills works end to end |
| **P2** | projects CRUD, `create_project`, requirements, discovery filters, Browse and Detail pages | scaffold, gen-types, schema-form | builder | new project auto-creates team + owner membership; filters work |
| **P3** | applications: apply, withdraw, decide (transaction); owner Applications tab | db-migrate, rule-tests | builder (architect reviews locking) | all §8 application tests pass, including the concurrent-accept test |
| **P4** | teams, tasks, assignment, remove/leave member, ownership transfer, task tree | rule-tests | builder | non-member assignment rejected; removed member's open tasks unassigned |
| **P5** | matching service, candidates tab, recommendations, skill-gap view | — | builder | breakdown sums to score; gap shown for seeded project |
| **P6** | analytics endpoints + `SchemaDashboard` + dashboard specs | schema-form, dataviz | builder / sql-scout (queries) | every §11 metric visible; numbers match seed |
| **P7** | test hardening, polish, README | rule-tests, code-review | builder / sql-scout | full suite green; README documents setup |

---

## 9. Testing

**Backend:** `pytest` + `httpx.AsyncClient` against the Docker MySQL. Each test runs in a fresh schema (fixture runs `db-migrate` reset + seed). There is one test per design-doc §21 item:

| Area | Tests |
|---|---|
| Users/skills | duplicate email → 409; duplicate skill → 409; `Python` vs `python ` → 409; proficiency update |
| Projects | create → team + owner membership exist; deadline before creation → 422; closed project blocks applications |
| Applications | valid apply; self-apply → 422; duplicate pending → 409; reapply after reject OK; non-owner decide → 403; reject creates no membership; withdraw; accept at capacity → 409; **two concurrent accepts at capacity − 1 → exactly one succeeds** |
| Teams | accepted user is a member; duplicate active membership blocked; second team for a project blocked; role and date stored |
| Tasks | assign to member OK; non-member → 409; due date after deadline → 409; remove member → their non-Done tasks become unassigned |
| Analytics | acceptance rate excludes Pending and Withdrawn; demand/supply counts match seed; skill gap reported for seeded gap project |
| Matching | score = sum of breakdown; candidate with no required skills has coverage 0 |

**Frontend:** `tsc --noEmit`, ESLint (150-LOC cap), and a vitest test per spec in `specs/forms/` that checks every field renders and required-field validation fires.

---

## 10. Commands

```bash
docker compose up -d db                       # MySQL 8
docker compose exec -T db mysql -uroot -p$MYSQL_ROOT_PASSWORD < db/001_schema.sql   # (db-migrate skill wraps all files)
cd api && uv run uvicorn app.main:app --reload
cd api && uv run pytest -q
cd web && npm run gen && npm run dev
cd web && npm run lint && npx tsc --noEmit && npx vitest run
```
