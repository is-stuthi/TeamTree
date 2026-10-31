# TeamTREE — Implementation Plan

> Companion to [docs/TeamTREE_Design_Document.md](docs/TeamTREE_Design_Document.md).
> The design doc says **what** and **why**. This file says **how**, in what order, with which tooling, and **where each rubric mark comes from**.

**Stack:** MySQL 8 (relational) · Neo4j 5 (graph + vector, the NoSQL component) · FastAPI (Python 3.12, raw SQL + Cypher) · Next.js 15 App Router + TypeScript + shadcn/ui · Docker Compose

---

## 0. Rubric map (DBMS Level 3, 50 marks)

Every row must be demonstrable in the viva. The `rubric-check` skill walks this table.

| # | Rubric component | Marks | Deliverable (evidence) | Section |
|---|---|---|---|---|
| 1 | ER diagram | 2 | `docs/ER Diagram.png` redrawn for schema v2 (Chen notation) + `docs/er.mmd` Mermaid source | §11 |
| 2 | Relational schema: keys, relationships, constraints | 3 | `docs/RELATIONAL_SCHEMA.md`: every relation with PK/FK/UNIQUE/CHECK, FDs, 3NF argument | §3, §11 |
| 3 | SQL DDL with constraints | 4 | `db/001_schema.sql` (PK, FK with chosen ON DELETE, UNIQUE, CHECK, generated columns, ENUMs) | §3.1 |
| 4 | NoSQL/Vector database creation | 4 | `graph/001_constraints.cypher`, `graph/002_vector_indexes.cypher`, initial load by `api/scripts/sync_graph.py --full` | §5.1–5.3 |
| 5 | Technology justification | 1 | `docs/TECH_JUSTIFICATION.md` | §11 |
| 6 | DML operations | 4 | `db/queries/dml_demo.sql` + every write endpoint (INSERT, UPDATE, DELETE, INSERT…SELECT, UPDATE…JOIN, soft delete) | §4.1 |
| 7 | Nested / correlated / recursive / join queries | 4 | `db/queries/catalogue.sql` Q1–Q12, each labelled and wired to an endpoint | §4.2 |
| 8 | Procedure/function, trigger, CTE | 6 | `db/002_functions.sql`, `db/003_triggers.sql`, `db/004_procedures.sql`, recursive and non-recursive CTEs in `db/005_views.sql` and the catalogue | §3.2–3.5, §4.2 |
| 9 | NoSQL/Vector feature: Read, Update, Delete | 7 | FastAPI `graph` router: Cypher reads (network, recommendations, shortest path, related skills, **vector semantic search**), updates (endorsements, skill relations, re-embed), deletes; used by `/graph/*` Next.js pages | §5.4 |
| 10 | Next.js interface | 3 | `web/`: Next.js App Router + shadcn + schema-driven forms and dashboards | §7 |
| 11 | Backend/API + database integration | 2 | FastAPI → MySQL (procedures, views) and → Neo4j (driver), with a MySQL → Neo4j sync service | §8, §5.5 |
| 12 | Auth (frontend) + ≥ 2 roles + RBAC in DB | 4 | JWT login/register UI; app roles `admin`/`member`; **MySQL `CREATE ROLE`/`GRANT`** (`db/007_rbac.sql`) incl. column-level privileges; role checks inside procedures; `middleware.ts` route guards | §6 |
| 13 | Documentation, Git/GitHub | 2 | `README.md`, this file, `docs/*`, GitHub repo with branch-per-phase PRs and conventional commits | §11 |
| 14 | Originality, individual contribution, viva | 4 | `docs/CONTRIBUTIONS.md` (one vertical slice per member), `docs/VIVA_NOTES.md` | §11 |

---

## 1. Working rules (apply to every phase)

| Rule | What it means in practice |
|---|---|
| **Skills first** | Repetitive workflows live in `.claude/skills/*` and load on demand. `CLAUDE.md` only points to them. |
| **Model routing** | Subagents in `.claude/agents/`: `sql-scout` (Haiku), `builder` (Sonnet), `architect` (Opus). See §9. |
| **shadcn only** | UI primitives come from `npx shadcn@latest add <name>` into `web/components/ui/`. Nothing hand-rolled. |
| **Schema-driven UI** | Forms and dashboards are JSON specs in `web/specs/`, rendered by static client components (`SchemaForm`, `SchemaDashboard`). Adding a form means writing JSON, not JSX. |
| **Atomic components** | Every custom `.ts`/`.tsx`/`.py` file stays at ≤ 150 lines. ESLint `max-lines` enforces this for TS; review enforces it for Python. Split files that grow past it. |
| **Generators for boilerplate** | Use the shadcn CLI, `openapi-typescript`, `json-schema-to-typescript` and `plop` (router, component, page). |
| **TS defs over source** | Learn the API contract from `web/lib/api/schema.d.ts` + `ui-schemas.d.ts`, not `api/app/**`. Regenerate them with the `gen-types` skill. |

---

## 2. Repository layout

```
TeamTree/
├── README.md  CLAUDE.md  IMPLEMENTATION.md  docker-compose.yml  .env.example
├── .claude/{agents,skills}/
├── docs/       TeamTREE_Design_Document.md  ER Diagram.png  er.mmd  RELATIONAL_SCHEMA.md
│               TECH_JUSTIFICATION.md  CONTRIBUTIONS.md  VIVA_NOTES.md  screenshots/
├── raw/schema.sql                 # v1, kept for history
├── db/
│   ├── 001_schema.sql  002_functions.sql  003_triggers.sql  004_procedures.sql
│   ├── 005_views.sql   006_indexes.sql    007_rbac.sql      seed.sql
│   └── queries/  catalogue.sql  dml_demo.sql          # rubric demo files (not part of migrate)
├── graph/
│   ├── 001_constraints.cypher  002_vector_indexes.cypher  003_demo_queries.cypher
├── api/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py  db.py  auth.py  errors.py  settings.py
│   │   ├── models/                 # Pydantic (source of truth → OpenAPI + UI specs)
│   │   ├── queries/                # SQL strings per router (keeps routers small)
│   │   ├── routers/                # auth users skills projects applications teams tasks matching analytics admin graph ui_schemas
│   │   ├── graph/  driver.py  sync.py  cypher.py  embed.py
│   │   ├── services/matching.py
│   │   └── ui_schemas/
│   ├── scripts/  dump_openapi.py  sync_graph.py
│   └── tests/
└── web/                           # Next.js 15 App Router
    ├── app/  (public)/  (dashboard)/  graph/  admin/  analytics/  api/session/route.ts
    ├── components/  ui/ (shadcn)  schema/  app/  graph/
    ├── lib/  api/{client.ts, schema.d.ts*, ui-schemas.d.ts*}  auth.ts      (* generated)
    ├── specs/  forms/*.json  dashboards/*.json
    ├── middleware.ts  plopfile.mjs  plop-templates/  components.json  eslint.config.mjs
```

---

## 3. MySQL — schema v2

### 3.0 Changes from v1 (`raw/schema.sql`)

| Area | v1 | v2 | Reason (design doc) |
|---|---|---|---|
| `Users.password` | plaintext name | `password_hash` | §12.1 |
| `Users.is_admin` | boolean | `role ENUM('admin','member')` | rubric 12, at least two roles |
| `Users` | — | `is_active`, `experience_level`, `availability` ENUM | §6.1, §10, §13.13 |
| `Project.status` | Planning/Active/Completed/Cancelled | **Open/Ongoing/Completed/Closed** | §6.3, rule 16 |
| `Project` | — | `max_team_size` (includes owner), `CHECK deadline ≥ creation` | §13.3, rule 15 |
| FKs to `Users`/`Project` | CASCADE | RESTRICT (soft delete) | §13.12–13 |
| `Skill` | case-sensitive unique | generated `s_name_norm` UNIQUE; `category` | rule 8 |
| `Requires` PK | (s_id, p_id) | (p_id, s_id, req_role) | §14.1 |
| `Team.p_id` | not unique | UNIQUE | 1:1 |
| `Joins` | composite PK | surrogate `j_id`, `leave_date`, one active row per (team, user) | §13.8 |
| `Application` | no Withdrawn, stored reviewer | adds Withdrawn; reviewer derived; one Pending per (user, project) | §7.6, rule 20 |
| new | — | `Ownership_Transfer` audit table | §13.10 |

**Policies decided:**
- The owner is automatically a team member with role `Owner` and counts toward capacity.
- A user can reapply after Rejected or Withdrawn.
- Membership history is preserved.
- The skill catalogue is admin-only.

**Project status meanings:**
- `Open`: recruiting; accepts applications.
- `Ongoing`: work started; no new applications.
- `Completed`: delivered.
- `Closed`: archived (soft delete).
- *Overdue* is derived, not stored.

"One active row" rules use a generated flag column, `IF(active,1,NULL)`, inside a UNIQUE index: many NULL (inactive) rows are allowed, but only one active row.

### 3.1 `db/001_schema.sql`

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
    role             ENUM('admin','member') NOT NULL DEFAULT 'member',
    bio              TEXT         NULL,
    location         VARCHAR(150) NULL,
    u_photo          VARCHAR(255) NULL,
    dob              DATE         NULL,                     -- age is derived, never stored
    experience_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL DEFAULT 'Beginner',
    availability     ENUM('Full-time','Part-time','Weekends','Unavailable') NOT NULL DEFAULT 'Part-time',
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    CONSTRAINT chk_users_email CHECK (email LIKE '%_@_%._%')
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

CREATE TABLE Requires (                                     -- PROJECT —REQUIRES— SKILL (M:N)
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

CREATE TABLE user_has_skill (                               -- USER —HAS— SKILL (M:N)
    u_id      INT NOT NULL,
    s_id      INT NOT NULL,
    u_s_level ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL,
    PRIMARY KEY (u_id, s_id),
    CONSTRAINT fk_uhs_user  FOREIGN KEY (u_id) REFERENCES Users(id)   ON DELETE CASCADE,
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

CREATE TABLE Joins (                                        -- USER —JOINS— TEAM (M:N, with history)
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

CREATE TABLE Task (                                         -- PROJECT —CONTAINS— TASK, USER —ASSIGNED— TASK
    task_id        INT AUTO_INCREMENT PRIMARY KEY,
    p_id           INT          NOT NULL,
    u_id           INT          NULL,                       -- NULL = unassigned
    parent_task_id INT          NULL,                       -- subtasks → recursive CTE
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

CREATE TABLE Application (                                  -- USER —SUBMITS— APPLICATION —FOR— PROJECT
    a_id          INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id  INT      NOT NULL,
    p_id          INT      NOT NULL,
    msg           TEXT     NULL,
    status        ENUM('Pending','Accepted','Rejected','Withdrawn') NOT NULL DEFAULT 'Pending',
    a_date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decision_date DATETIME NULL,                            -- attribute of REVIEWS
    pending_flag  TINYINT AS (IF(status = 'Pending', 1, NULL)) STORED,
    UNIQUE KEY uq_application_pending (applicant_id, p_id, pending_flag),
    CONSTRAINT fk_application_applicant FOREIGN KEY (applicant_id) REFERENCES Users(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_application_project   FOREIGN KEY (p_id)         REFERENCES Project(p_id) ON DELETE RESTRICT,
    CONSTRAINT chk_application_decision CHECK (
        (status IN ('Pending','Withdrawn') AND decision_date IS NULL) OR
        (status IN ('Accepted','Rejected') AND decision_date IS NOT NULL))
) ENGINE=InnoDB;
-- Reviewer = Project.owner_id (derived through p_id). No reviewer_id column.

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
```

### 3.2 `db/002_functions.sql` (stored functions)

```sql
DELIMITER $$
CREATE FUNCTION fn_level_ord(lvl VARCHAR(20)) RETURNS TINYINT DETERMINISTIC NO SQL
RETURN CASE lvl WHEN 'Beginner' THEN 1 WHEN 'Intermediate' THEN 2
                WHEN 'Advanced' THEN 3 WHEN 'Expert' THEN 4 ELSE 0 END$$

CREATE FUNCTION fn_is_active_member(p_pid INT, p_uid INT) RETURNS BOOLEAN READS SQL DATA
RETURN EXISTS (SELECT 1 FROM Joins j JOIN Team t ON t.t_id = j.t_id
                WHERE t.p_id = p_pid AND j.u_id = p_uid AND j.leave_date IS NULL)$$

CREATE FUNCTION fn_active_member_count(p_pid INT) RETURNS INT READS SQL DATA
RETURN (SELECT COUNT(*) FROM Joins j JOIN Team t ON t.t_id = j.t_id
         WHERE t.p_id = p_pid AND j.leave_date IS NULL)$$

-- Denominator = decided applications only (excludes Pending and Withdrawn, design doc §11.5)
CREATE FUNCTION fn_acceptance_rate(p_pid INT) RETURNS DECIMAL(5,4) READS SQL DATA
RETURN (SELECT SUM(status = 'Accepted') / NULLIF(SUM(status IN ('Accepted','Rejected')), 0)
          FROM Application WHERE p_id = p_pid)$$

CREATE FUNCTION fn_is_admin(p_uid INT) RETURNS BOOLEAN READS SQL DATA
RETURN EXISTS (SELECT 1 FROM Users WHERE id = p_uid AND role = 'admin' AND is_active)$$
DELIMITER ;
```

### 3.3 `db/003_triggers.sql`

Triggers do **validation only** and never write other rows (design doc §17.2).

```sql
DELIMITER $$
CREATE TRIGGER trg_application_bi BEFORE INSERT ON Application
FOR EACH ROW
BEGIN
    DECLARE v_owner INT; DECLARE v_status VARCHAR(10); DECLARE v_cap INT;
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

CREATE PROCEDURE validate_task(IN p_pid INT, IN p_uid INT, IN p_due DATE)
BEGIN
    DECLARE v_deadline DATE;
    IF p_uid IS NOT NULL AND NOT fn_is_active_member(p_pid, p_uid) THEN
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

CREATE TRIGGER trg_project_bu BEFORE UPDATE ON Project           -- lifecycle guard
FOR EACH ROW
BEGIN
    IF OLD.status IN ('Completed','Closed') AND NEW.status IN ('Open','Ongoing') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROJECT_REOPEN_FORBIDDEN';
    END IF;
END$$
DELIMITER ;
```

### 3.4 `db/004_procedures.sql`

Procedures run with the default `SQL SECURITY DEFINER` and are created by root. The low-privilege app user can therefore perform guarded writes, such as changing application status or inserting memberships, **only** through them (§6.3). Pattern:

```sql
DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
START TRANSACTION;  …validate (SIGNAL)…  …writes…  COMMIT;
```

| Procedure | Signature | Behaviour |
|---|---|---|
| `register_user` | `(f, m, l, email, hash, OUT id)` | Insert with role `member`. |
| `create_project` | `(owner, name, desc, deadline, max_size, OUT p_id)` | Project → Team → owner in Joins (`Owner`). One transaction. |
| `apply_to_project` | `(user, p_id, msg, OUT a_id)` | Insert; trigger + pending-unique index validate. |
| `decide_application` | `(a_id, actor, decision, role)` | §16.1 transaction (below). |
| `withdraw_application` | `(a_id, actor)` | Actor = applicant, Pending → Withdrawn. |
| `assign_task` | `(task_id, actor, assignee)` | Actor must be owner or active member; trigger checks the assignee. |
| `remove_member` / `leave_team` | `(p_id, actor, user)` | Set `leave_date`; unassign the user's non-Done tasks; owner can't be removed. |
| `transfer_ownership` | `(p_id, actor, new_owner)` | New owner must be an active member; swap roles; insert `Ownership_Transfer`. |
| `create_skill` / `update_skill` | `(actor, name, category)` | `fn_is_admin(actor)` or SIGNAL `NOT_ADMIN`. |
| `set_user_role` | `(actor, user, role)` | Admin only; can't demote the last active admin. |
| `deactivate_user` | `(actor, user)` | Self or admin; sets `is_active = FALSE`; closes the user's Open projects. |

```sql
DELIMITER $$
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
    SELECT p_id, applicant_id, status INTO v_pid, v_applicant, v_status
      FROM Application WHERE a_id = p_a_id FOR UPDATE;
    IF v_pid IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'APP_NOT_FOUND'; END IF;

    -- Lock the project row first: serialises concurrent accepts for the capacity check.
    SELECT owner_id, status, max_team_size INTO v_owner, v_pstatus, v_cap
      FROM Project WHERE p_id = v_pid FOR UPDATE;
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
        VALUES (v_tid, v_applicant, COALESCE(p_role, 'Member'), CURDATE());
    END IF;

    UPDATE Application SET status = p_decision, decision_date = NOW() WHERE a_id = p_a_id;
    COMMIT;
END$$
DELIMITER ;
```

If the membership insert fails, the exit handler rolls back the status change as well (§13.7).

### 3.5 `db/005_views.sql`

| View | Columns / purpose | DB concept shown |
|---|---|---|
| `OpenProjects` | open projects + owner + `GROUP_CONCAT` domains + `is_overdue` | JOIN, aggregation |
| `ProjectApplicationSummary` | counts per status, `fn_acceptance_rate(p_id)` | function in view |
| `UserSkillProfiles` | user × skill × level × category | JOIN |
| `ProjectSkillRequirements` | project × skill × role × level × count | JOIN |
| `TeamMemberDetails` | active + historical members | JOIN |
| `TaskProgressSummary` | per-project totals, % done, overdue | conditional aggregation |
| `TopInDemandSkills` | projects requiring vs users possessing, `RANK()` by ratio | **CTE + window function** |
| `SkillGap` | requirement vs active members meeting the level | LEFT JOIN, `fn_level_ord` |

```sql
CREATE OR REPLACE VIEW TopInDemandSkills AS
WITH demand AS (SELECT s_id, COUNT(DISTINCT p_id) AS projects_requiring FROM Requires GROUP BY s_id),
     supply AS (SELECT s_id, COUNT(*)             AS users_possessing   FROM user_has_skill GROUP BY s_id)
SELECT s.s_id, s.s_name, s.category,
       COALESCE(d.projects_requiring, 0) AS projects_requiring,
       COALESCE(u.users_possessing, 0)   AS users_possessing,
       COALESCE(d.projects_requiring, 0) / NULLIF(u.users_possessing, 0) AS demand_supply_ratio,
       RANK() OVER (ORDER BY COALESCE(d.projects_requiring, 0) DESC) AS demand_rank
FROM Skill s LEFT JOIN demand d USING (s_id) LEFT JOIN supply u USING (s_id);

CREATE OR REPLACE VIEW SkillGap AS
SELECT r.p_id, r.s_id, s.s_name, r.req_role, r.p_s_level AS required_level, r.req_count,
       COUNT(DISTINCT uhs.u_id) AS members_with_skill,
       COUNT(DISTINCT CASE WHEN fn_level_ord(uhs.u_s_level) >= fn_level_ord(r.p_s_level)
                           THEN uhs.u_id END) AS qualified_members,
       GREATEST(r.req_count - COUNT(DISTINCT CASE WHEN fn_level_ord(uhs.u_s_level)
                >= fn_level_ord(r.p_s_level) THEN uhs.u_id END), 0) AS shortfall
FROM Requires r
JOIN Skill s                  ON s.s_id = r.s_id
LEFT JOIN Team t              ON t.p_id = r.p_id
LEFT JOIN Joins j             ON j.t_id = t.t_id AND j.leave_date IS NULL
LEFT JOIN user_has_skill uhs  ON uhs.u_id = j.u_id AND uhs.s_id = r.s_id
GROUP BY r.p_id, r.s_id, s.s_name, r.req_role, r.p_s_level, r.req_count;
```

### 3.6 `db/006_indexes.sql`

```sql
CREATE INDEX ix_users_name       ON Users (l_name, f_name);
CREATE INDEX ix_project_status   ON Project (status, deadline);
CREATE INDEX ix_project_owner    ON Project (owner_id);
CREATE INDEX ix_domain_name      ON Domain (d_name);
CREATE INDEX ix_requires_skill   ON Requires (s_id, p_s_level);
CREATE INDEX ix_uhs_skill        ON user_has_skill (s_id, u_s_level);
CREATE INDEX ix_application_proj ON Application (p_id, status);
CREATE INDEX ix_task_project     ON Task (p_id, status);
CREATE INDEX ix_task_user        ON Task (u_id, status);
CREATE INDEX ix_joins_user       ON Joins (u_id, leave_date);
```

Demo `EXPLAIN` before and after `ix_project_status` in the viva.

### 3.7 `db/seed.sql`
Seed data:
- About 15 users (2 admins).
- 25 skills in 5 categories.
- 10 projects covering every status, with descriptions rich enough for embeddings.
- Applications in every status.
- One project with a skill gap and one at capacity.
- A subtask tree three levels deep.

Generate it with `sql-scout` (Haiku).

---

## 4. SQL operations & query catalogue (rubric 6, 7, 8)

### 4.1 DML (`db/queries/dml_demo.sql`, also used by endpoints)

| # | Operation | Example | Endpoint |
|---|---|---|---|
| D1 | multi-row INSERT | add several skills to a profile | `PUT /users/me/skills` |
| D2 | INSERT … SELECT | copy requirements from an existing project ("use as template") | `POST /projects/{id}/requirements/copy-from/{src}` |
| D3 | UPDATE with JOIN | mark open tasks `Blocked` for projects just set to `Closed` | `PATCH /projects/{id}` (status → Closed) |
| D4 | UPDATE (soft delete) | `Users.is_active = FALSE` | `POST /users/me/deactivate` |
| D5 | DELETE | remove a skill from a profile / remove a requirement | `DELETE /users/me/skills/{s_id}` |
| D6 | UPSERT | `INSERT … ON DUPLICATE KEY UPDATE u_s_level = VALUES(u_s_level)` | `PUT /users/me/skills/{s_id}` |
| D7 | transaction via procedure | `CALL decide_application(…)` | `POST /applications/{id}/decision` |

### 4.2 Query catalogue (`db/queries/catalogue.sql`)

Each query has a header comment, `-- Q4 [NESTED + NOT EXISTS / relational division] …`, so evaluators can find it.

| # | Type | Question answered | Used by |
|---|---|---|---|
| Q1 | multi-way JOIN (5 tables) | project detail: owner, domains, requirements, team size | `GET /projects/{id}` |
| Q2 | LEFT JOIN + GROUP BY + HAVING | projects with zero applications | analytics |
| Q3 | nested `IN` | users having *any* skill required by project X | candidates prefilter |
| Q4 | nested `NOT EXISTS` (relational division) | users possessing **every** skill project X requires at the required level | `GET /projects/{id}/candidates?full=1` |
| Q5 | **correlated** subquery | team members who completed more tasks than their team's average | team analytics |
| Q6 | **correlated** `EXISTS` | Open projects where the current user meets ≥ 1 requirement | `GET /users/me/recommended-projects` |
| Q7 | correlated scalar subquery in SELECT | each user's strongest skill | profile card |
| Q8 | **recursive CTE** | subtask tree with depth and path | `GET /projects/{id}/tasks/tree` |
| Q9 | **recursive CTE** (date series) | applications per day for the last 30 days, gaps filled with 0 | analytics timeline |
| Q10 | CTE + window (`RANK`, `ROW_NUMBER`) | top 3 in-demand skills per category | analytics |
| Q11 | self-join | pairs of users who share a team → collaborator edges | Neo4j sync (§5.5) |
| Q12 | `UNION ALL` + ORDER | user activity feed (applications, joins, tasks) | dashboard |

Key examples:

```sql
-- Q4 [NESTED + NOT EXISTS: relational division]
SELECT u.id, u.f_name, u.l_name FROM Users u
WHERE u.is_active AND u.id <> (SELECT owner_id FROM Project WHERE p_id = :pid)
  AND NOT EXISTS (
    SELECT 1 FROM Requires r WHERE r.p_id = :pid
      AND NOT EXISTS (
        SELECT 1 FROM user_has_skill h
         WHERE h.u_id = u.id AND h.s_id = r.s_id
           AND fn_level_ord(h.u_s_level) >= fn_level_ord(r.p_s_level)));

-- Q5 [CORRELATED]
SELECT j.u_id, t.p_id, COUNT(tk.task_id) AS done
FROM Joins j JOIN Team t ON t.t_id = j.t_id
JOIN Task tk ON tk.p_id = t.p_id AND tk.u_id = j.u_id AND tk.status = 'Done'
WHERE j.leave_date IS NULL
GROUP BY j.u_id, t.p_id
HAVING COUNT(tk.task_id) > (
    SELECT COUNT(*) / NULLIF(COUNT(DISTINCT t2.u_id), 0)
    FROM Task t2 WHERE t2.p_id = t.p_id AND t2.status = 'Done');

-- Q8 [RECURSIVE CTE]
WITH RECURSIVE tree AS (
  SELECT task_id, parent_task_id, t_name, status, 0 AS depth, CAST(t_name AS CHAR(500)) AS path
  FROM Task WHERE p_id = :pid AND parent_task_id IS NULL
  UNION ALL
  SELECT c.task_id, c.parent_task_id, c.t_name, c.status, tree.depth + 1,
         CONCAT(tree.path, ' › ', c.t_name)
  FROM Task c JOIN tree ON c.parent_task_id = tree.task_id
) SELECT * FROM tree ORDER BY path;

-- Q9 [RECURSIVE CTE: date series]
WITH RECURSIVE days AS (
  SELECT CURDATE() - INTERVAL 29 DAY AS d UNION ALL SELECT d + INTERVAL 1 DAY FROM days WHERE d < CURDATE()
) SELECT days.d, COUNT(a.a_id) AS applications
  FROM days LEFT JOIN Application a ON DATE(a.a_date) = days.d GROUP BY days.d ORDER BY days.d;

-- Q11 [SELF-JOIN]
SELECT LEAST(a.u_id, b.u_id) AS u1, GREATEST(a.u_id, b.u_id) AS u2, COUNT(DISTINCT a.t_id) AS shared_teams
FROM Joins a JOIN Joins b ON a.t_id = b.t_id AND a.u_id < b.u_id
GROUP BY u1, u2;
```

---

## 5. Neo4j — graph + vector (rubric 4, 9)

### 5.1 Why a graph (summary for `docs/TECH_JUSTIFICATION.md`)
Multi-hop questions are awkward and slow as recursive SQL self-joins: "friends of collaborators with complementary skills", "shortest collaboration path between two people", "skills related to the one we're missing". Neo4j answers them natively. Neo4j 5 also has **built-in vector indexes**, so semantic search over project descriptions needs no extra vector database.

**Division of responsibility:**
- MySQL is the system of record for transactional data: users, projects, applications, teams, tasks.
- Neo4j holds a projection of that data, plus graph-only data that doesn't exist in MySQL: **endorsements**, **skill-to-skill relations** and **embeddings**.

### 5.2 Graph model

```
(:User {id, name, availability, embedding[384]})
(:Skill {id, name, category})
(:Project {id, name, status, domains[], embedding[384]})

(User)-[:HAS_SKILL {level}]->(Skill)
(Project)-[:REQUIRES {level, role, count}]->(Skill)
(User)-[:MEMBER_OF {role, active}]->(Project)
(User)-[:OWNS]->(Project)
(User)-[:COLLABORATED_WITH {shared}]-(User)          // derived from Q11
(User)-[:ENDORSES {skill_id, weight 1..5, note, at}]->(User)   // graph-only
(Skill)-[:RELATED_TO {weight 0..1}]-(Skill)                    // graph-only, admin-curated
```

### 5.3 Creation scripts

`graph/001_constraints.cypher`
```cypher
CREATE CONSTRAINT user_id    IF NOT EXISTS FOR (u:User)    REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT skill_id   IF NOT EXISTS FOR (s:Skill)   REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE INDEX skill_name      IF NOT EXISTS FOR (s:Skill)   ON (s.name);
CREATE INDEX project_status  IF NOT EXISTS FOR (p:Project) ON (p.status);
```

`graph/002_vector_indexes.cypher`
```cypher
CREATE VECTOR INDEX project_embedding IF NOT EXISTS FOR (p:Project) ON p.embedding
OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } };
CREATE VECTOR INDEX user_embedding IF NOT EXISTS FOR (u:User) ON u.embedding
OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } };
```

**Embeddings** (`api/app/graph/embed.py`) use `sentence-transformers/all-MiniLM-L6-v2`: local, free, 384 dimensions, loaded once at startup.
- Project text = name + description + domains + required skills.
- User text = bio + skills with levels.

Initial load: `uv run python scripts/sync_graph.py --full` reads MySQL, `MERGE`s every node and relationship, and computes embeddings.

### 5.4 RUD features (FastAPI `routers/graph.py`, Cypher in `app/graph/cypher.py`)

| Op | Endpoint | Cypher idea | UI |
|---|---|---|---|
| **R** | `GET /graph/users/{id}/network?depth=2` | `MATCH p=(u:User {id:$id})-[:COLLABORATED_WITH*1..2]-(o) RETURN p` → nodes/edges JSON | `/graph/network` force graph |
| **R** | `GET /graph/users/{id}/recommended-collaborators` | friends-of-collaborators not yet connected, ranked by complementary skills + endorsements | dashboard card |
| **R** | `GET /graph/path?from=&to=` | `shortestPath((a)-[:COLLABORATED_WITH*..6]-(b))` | "how am I connected?" |
| **R** | `GET /graph/skills/{id}/related` | `RELATED_TO` edges + co-occurrence (skills held together by ≥ N users) | skill-gap tab suggestions |
| **R** | `GET /graph/projects/{id}/gap-candidates` | for each MySQL `SkillGap` shortfall: users with that skill or a `RELATED_TO` skill, ordered by endorsement weight | owner Candidates tab |
| **R (vector)** | `GET /graph/search/projects?q=` | embed `q` → `CALL db.index.vector.queryNodes('project_embedding', 10, $vec)` filtered to Open | `/graph/search` |
| **R (vector)** | `GET /graph/projects/{id}/similar` and `GET /graph/users/{id}/similar` | query the index with the node's own embedding | project page "Similar projects" |
| **U** | `PUT /graph/endorsements` `{to, skill_id, weight, note}` | `MERGE (a)-[e:ENDORSES {skill_id:$sid}]->(b) SET e.weight=$w, e.note=$n, e.at=datetime()`; only if `COLLABORATED_WITH` exists | profile "Endorse" dialog |
| **U** | `PUT /graph/skills/{a}/related/{b}` `{weight}` (admin) | `MERGE (a)-[r:RELATED_TO]-(b) SET r.weight=$w` | `/admin/skills` |
| **U** | `POST /graph/projects/{id}/reembed` (owner) | recompute and `SET p.embedding` | after editing a project |
| **D** | `DELETE /graph/endorsements/{to}/{skill_id}` | `MATCH (a)-[e:ENDORSES {skill_id:$sid}]->(b) DELETE e` | profile |
| **D** | `DELETE /graph/skills/{a}/related/{b}` (admin) | delete the `RELATED_TO` edge | `/admin/skills` |
| **D** | sync on member removal / user deactivation | `SET m.active=false` / `DETACH DELETE` user node on anonymisation | automatic |

```cypher
// Recommended collaborators
MATCH (me:User {id:$uid})-[:COLLABORATED_WITH]-(mid:User)-[:COLLABORATED_WITH]-(c:User)
WHERE c <> me AND NOT (me)-[:COLLABORATED_WITH]-(c)
WITH me, c, count(DISTINCT mid) AS mutual
OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill) WHERE NOT (me)-[:HAS_SKILL]->(s)
OPTIONAL MATCH (:User)-[e:ENDORSES]->(c)
RETURN c.id AS id, c.name AS name, mutual,
       collect(DISTINCT s.name)[..5] AS complementary_skills,
       coalesce(avg(e.weight), 0) AS endorsement_score
ORDER BY mutual DESC, size(complementary_skills) DESC LIMIT 10;

// Semantic project search
CALL db.index.vector.queryNodes('project_embedding', 20, $vec) YIELD node, score
WHERE node.status = 'Open'
RETURN node.id AS id, node.name AS name, score ORDER BY score DESC LIMIT 10;
```

`graph/003_demo_queries.cypher` collects these queries for showing in the Neo4j Browser during the viva.

### 5.5 Sync (MySQL → Neo4j)
- `app/graph/sync.py` provides idempotent `MERGE` functions: `upsert_user`, `upsert_user_skills`, `upsert_project` (+ embedding), `upsert_membership` (also rebuilds that team's `COLLABORATED_WITH` edges via Q11), `deactivate_membership`, `delete_user`.
- Routers call sync **after** the MySQL procedure commits. MySQL is never rolled back because Neo4j failed: the failure is logged, and `scripts/sync_graph.py --full` reconciles. That is acceptable because Neo4j only holds a projection plus graph-only data.
- Graph-only data (endorsements, RELATED_TO) is never overwritten by sync.

---

## 6. Authentication & authorization (rubric 12)

### 6.1 Roles

| Role | Where it's stored | Can |
|---|---|---|
| `admin` | `Users.role` | manage the skill catalogue and RELATED_TO edges, change user roles, deactivate users, view all analytics |
| `member` | `Users.role` (default) | profile, skills, create projects, apply, endorse collaborators |
| *owner* (contextual) | `Project.owner_id` | manage own project: requirements, decisions, team, tasks, re-embed |
| *team member* (contextual) | active `Joins` row | view and update tasks of that project |

### 6.2 Flow
1. `register`/`login` pages are `SchemaForm` specs. Next.js route handler `app/api/session/route.ts` POSTs to FastAPI `/auth/login`.
2. FastAPI verifies bcrypt and returns a JWT `{sub, role, exp}` (HS256, `JWT_SECRET`). Next.js stores it in an **httpOnly, SameSite=Lax cookie** `tt_session`.
3. `web/middleware.ts` verifies the JWT with `jose`. It redirects anonymous users away from `/dashboard/*`, `/graph/*` and `/analytics`, and non-admins away from `/admin/*`.
4. Server Components forward the cookie as `Authorization: Bearer` to FastAPI. Client components call FastAPI through the `/api/proxy/[...path]` route handler, so the token never reaches JS.
5. FastAPI uses `current_user` and `require_role("admin")` dependencies. Ownership checks live in the procedures (the `actor` argument).

### 6.3 RBAC **in the database** (`db/007_rbac.sql`, applied as root)

```sql
CREATE ROLE IF NOT EXISTS 'tt_admin', 'tt_member_app', 'tt_analyst';

GRANT ALL PRIVILEGES ON teamtree.* TO 'tt_admin';

-- Application role: read everything, write only where safe; guarded writes go through procedures
GRANT SELECT, EXECUTE ON teamtree.* TO 'tt_member_app';
GRANT INSERT, UPDATE, DELETE ON teamtree.user_has_skill TO 'tt_member_app';
GRANT INSERT, UPDATE, DELETE ON teamtree.Requires       TO 'tt_member_app';
GRANT INSERT, DELETE         ON teamtree.Domain         TO 'tt_member_app';
GRANT INSERT, UPDATE         ON teamtree.Task           TO 'tt_member_app';
GRANT UPDATE (p_name, description, deadline, status, max_team_size)   -- column-level privilege:
             ON teamtree.Project TO 'tt_member_app';                  -- owner_id only via transfer_ownership
-- NO INSERT/UPDATE on Application, Joins, Team, Skill, Ownership_Transfer, Users.role/is_active,
-- and no INSERT on Users (register_user): these change only through DEFINER procedures.
GRANT UPDATE (f_name, m_name, l_name, bio, location, u_photo, dob, experience_level, availability, password_hash)
             ON teamtree.Users TO 'tt_member_app';

-- Read-only reporting role: views only
GRANT SELECT ON teamtree.OpenProjects              TO 'tt_analyst';
GRANT SELECT ON teamtree.ProjectApplicationSummary TO 'tt_analyst';
GRANT SELECT ON teamtree.TopInDemandSkills         TO 'tt_analyst';
GRANT SELECT ON teamtree.TaskProgressSummary       TO 'tt_analyst';
GRANT SELECT ON teamtree.SkillGap                  TO 'tt_analyst';

CREATE USER IF NOT EXISTS 'tt_app'@'%'    IDENTIFIED BY '${TT_APP_PASSWORD}';
CREATE USER IF NOT EXISTS 'tt_report'@'%' IDENTIFIED BY '${TT_REPORT_PASSWORD}';
GRANT 'tt_member_app' TO 'tt_app'@'%';    SET DEFAULT ROLE 'tt_member_app' TO 'tt_app'@'%';
GRANT 'tt_analyst'    TO 'tt_report'@'%'; SET DEFAULT ROLE 'tt_analyst'    TO 'tt_report'@'%';
```

`${…}` placeholders are substituted from `.env` by the `db-migrate` skill and never committed. FastAPI connects as **`tt_app`**. The analytics dashboard connects as `tt_report`.

**Viva demo:**
- As `tt_app`, `UPDATE Application SET status='Accepted' …` fails with error 1142 (command denied).
- `CALL decide_application(…)` succeeds for the owner and fails with `NOT_OWNER` for anyone else.
- `SHOW GRANTS FOR 'tt_app'@'%' USING 'tt_member_app';` shows the privileges.

---

## 7. Frontend — Next.js 15 App Router + shadcn (rubric 10)

### 7.1 Setup (generated)
```bash
npx create-next-app@latest web --ts --eslint --tailwind --app --src-dir=false --import-alias "@/*"
cd web && npx shadcn@latest init
npx shadcn@latest add button card input textarea select checkbox badge table tabs dialog form label \
    sonner calendar popover chart skeleton separator dropdown-menu avatar progress sheet command
npm i openapi-fetch @tanstack/react-query react-hook-form zod @hookform/resolvers jose react-force-graph-2d
npm i -D openapi-typescript json-schema-to-typescript plop vitest @testing-library/react
```
`eslint.config.mjs` adds:
`{ files: ["**/*.{ts,tsx}"], ignores: ["components/ui/**", "lib/api/*.d.ts"], rules: { "max-lines": ["error", { max: 150, skipBlankLines: true, skipComments: true }] } }`

### 7.2 Routes

| Route | Kind | Composition |
|---|---|---|
| `/` | public | landing + stats `SchemaDashboard` (`public_stats`) |
| `/login`, `/register` | public | `SchemaForm` |
| `/projects`, `/projects/[id]` | public | filter `SchemaForm`, `ProjectCard` grid; detail with requirements `Table`, Apply `Dialog`, "Similar projects" (vector) |
| `/dashboard` (+ `/skills`, `/projects`, `/applications`, `/teams`, `/tasks`) | member | `Tabs` of specs and tables; activity feed (Q12) |
| `/projects/[id]/manage/*` | owner | requirements, applications (accept/reject), team, tasks (tree via Q8), candidates (SQL score + graph gap-candidates), skill gap dashboard |
| `/graph/network`, `/graph/search` | member | `NetworkGraph` (react-force-graph, `dynamic(..., {ssr:false})`), semantic search box |
| `/users/[id]` | member | profile, endorsements (U/D), "how am I connected" path |
| `/analytics` | member (admin sees all) | `SchemaDashboard` (`analytics`) |
| `/admin/skills`, `/admin/users` | **admin** | skill catalogue CRUD, RELATED_TO editor, role changes |

### 7.3 Schema renderers (client components, ≤ 150 LOC each)

```
components/schema/
  SchemaForm.tsx  buildZod.ts  FieldRenderer.tsx  useSpec.ts
  field/  TextField  TextareaField  NumberField  SelectField  DateField  TagsField  SkillLevelField  PasswordField
  SchemaDashboard.tsx  WidgetRenderer.tsx
  widget/ StatWidget  BarWidget  PieWidget  LineWidget  TableWidget  ProgressWidget  GraphWidget
```

| `ui.widget` | shadcn component |
|---|---|
| default string | `Input` |
| `textarea` | `Textarea` |
| `number` | `Input type=number` |
| enum | `Select` |
| `date` | `Popover` + `Calendar` |
| `checkbox` | `Checkbox` |
| `tags` | `Input` + `Badge` |
| `skill-level` | `Select` × 2 rows |
| `password` | `Input type=password` |

Dashboard widgets: `stat`, `bar`, `pie`, `line` (Q9 timeline), `table`, `progress`, `graph` (Neo4j network). Charts use shadcn `chart` (Recharts) and follow the `dataviz` skill.

Example form spec (served by FastAPI `GET /ui-schemas/project_create`):
```json
{
  "name": "project_create", "title": "Create project",
  "submit": { "method": "POST", "path": "/projects" },
  "schema": { "$ref": "#/components/schemas/ProjectCreate" },
  "ui": { "order": ["p_name", "description", "domains", "deadline", "max_team_size"],
          "fields": { "description": { "widget": "textarea", "rows": 5 }, "domains": { "widget": "tags" },
                      "deadline": { "widget": "date", "minDate": "today" },
                      "max_team_size": { "widget": "number", "help": "Includes you (the owner)" } } }
}
```

### 7.4 API access
`lib/api/client.ts` creates an `openapi-fetch` client typed with `paths` from the generated `schema.d.ts`. There are no hand-written fetch wrappers. Server Components use `serverApi()`, which attaches the cookie token; client components go through `/api/proxy`.

---

## 8. Backend — FastAPI (rubric 11)

- `db.py` runs an `aiomysql` pool as `tt_app` with helpers `call_proc`, `fetch_all`, `fetch_one`. `graph/driver.py` holds a Neo4j async driver singleton.
- **Endpoints:**
  - `auth`: register, login, me.
  - `users`: me, profile, skills (D1, D5, D6), deactivate.
  - `skills`: list, search.
  - `projects`: CRUD via `create_project` and Q1, filters, requirements (D2), transfer.
  - `applications`: apply, list, decide (D7), withdraw.
  - `teams`: view, remove, leave.
  - `tasks`: CRUD, assign, tree (Q8).
  - `matching`: candidates (Q3/Q4 + weighted score), recommended projects (Q6), skill gap.
  - `analytics`: views + Q2, Q5, Q9, Q10, Q12.
  - `admin`: skills, roles, users.
  - `graph`: §5.4.
  - `ui_schemas`.
- **Matching score** uses design doc §10 weights: coverage 50, proficiency 20, experience 15, domain 10, availability 5. It returns a per-factor breakdown and is labelled "indicative". The candidate list also shows the Neo4j endorsement score.
- `errors.py` maps errors to HTTP statuses:

| Error | HTTP |
|---|---|
| `NOT_OWNER`, `NOT_ADMIN`, MySQL 1142/1143 (permission denied) | 403 |
| `APP_NOT_FOUND` | 404 |
| `PROJECT_NOT_OPEN`, `PROJECT_FULL`, `APP_NOT_PENDING`, `ASSIGNEE_NOT_MEMBER`, `TASK_AFTER_DEADLINE`, `PROJECT_NOT_ACCEPTING`, `PROJECT_REOPEN_FORBIDDEN` | 409 |
| duplicate key on `uq_application_pending` | 409 `DUPLICATE_PENDING` |
| duplicate key on `uq_users_email` | 409 `EMAIL_TAKEN` |
| `SELF_APPLICATION`, `BAD_DECISION`, CHECK violation (3819) | 422 |

- **Codegen:** `scripts/dump_openapi.py` → `openapi-typescript` → `web/lib/api/schema.d.ts`, then `json2ts` → `ui-schemas.d.ts`. `npm run gen` runs both; CI runs `git diff --exit-code lib/api/`.

---

## 9. Skills, agents and model routing

| Skill | Loads when |
|---|---|
| `db-migrate` | SQL changes, DB reset/seed, RBAC apply |
| `neo4j-graph` | Cypher, sync, vector index, embeddings |
| `gen-types` | Pydantic or UI-schema changes |
| `scaffold` | new router, component or page; shadcn add; splitting a file over 150 LOC |
| `schema-form` | new or changed form or dashboard (JSON only) |
| `check-docker` | containers, MySQL/Neo4j health, ports, env |
| `rule-tests` | running and interpreting the test suite |
| `rubric-check` | before each phase demo and the final viva |

Built-in skills: `dataviz` (charts), `code-review` / `simplify` (end of each phase), `run` (launch and verify).

| Task | Agent | Model |
|---|---|---|
| simple questions, log/test summaries, basic SQL/Cypher reads, seed data, simple JSON specs | `sql-scout` | **Haiku** |
| features, routine edits, standard debugging, generators, tests | `builder` | **Sonnet** |
| schema/RBAC/transaction/locking design, MySQL ↔ Neo4j consistency, concurrency or infra failures | `architect` | **Opus** (plans only) |

**Escalation:** Haiku unsure → Sonnet. Sonnet fails twice, or the fix needs schema or transaction redesign → Opus writes a plan → Sonnet implements it.

---

## 10. Phases

Each phase has its own self-contained task file in [`phases/`](phases/README.md): goal, rubric rows, agent and skills, checklist, done criteria and demo. Load only the current phase file. Every phase ends with the same gate (tests, lint, type-gen diff, `code-review`, `rubric-check`), described in `phases/README.md`.

| Phase | Scope | Rubric rows |
|---|---|---|
| [P0](phases/P0-foundation.md) | Docker, MySQL v2 + functions/triggers/procedures/views/RBAC, Neo4j constraints + vector indexes, API/web skeletons, plop | 3, 4, 8, 12 |
| [P1](phases/P1-auth-users.md) | auth, roles, session cookie, middleware, profiles, skills, admin, `SchemaForm` | 10, 11, 12 |
| [P2](phases/P2-projects.md) | projects, requirements (D2), close cascade (D3), discovery (Q1, Q6) | 6, 7 |
| [P3](phases/P3-applications.md) | apply/withdraw/decide transaction, concurrency + rollback tests | 6, 8 |
| [P4](phases/P4-teams-tasks.md) | team history, tasks + tree (Q8), Q5, remove/leave, ownership transfer | 7, 8 |
| [P5](phases/P5-matching.md) | candidate scoring (Q3, Q4), Q7, skill gap | 7 |
| [P6](phases/P6-neo4j-graph.md) | Neo4j sync, embeddings, graph R/U/D, vector search, graph UI | 4, 9 |
| [P7](phases/P7-analytics.md) | analytics (Q2, Q9, Q10, Q12), `tt_report`, `SchemaDashboard` | 7, 10 |
| [P8](phases/P8-hardening.md) | full test matrix, CI, LOC audit, EXPLAIN, UX polish | all |
| [P9](phases/P9-docs-rubric.md) | ER redraw, relational schema doc, tech justification, README, contributions, viva | 1, 2, 5, 13, 14 |

P6 can run in parallel with P2–P5 once P1 is merged.

---

## 11. Documentation, Git & viva (rubric 1, 2, 5, 13, 14)

| File | Contents |
|---|---|
| `docs/ER Diagram.png` + `docs/er.mmd` | Chen ER for v2: add `role`, `max_team_size`, `leave_date`, `Withdrawn`, `Ownership_Transfer` (TRANSFERS relationship), derived `age`, multivalued `domain`, composite `name`; cardinality + participation |
| `docs/RELATIONAL_SCHEMA.md` | each relation: attributes, PK, FKs + ON DELETE rationale, UNIQUE/CHECK, FDs, 3NF/BCNF justification; ER → relation mapping table |
| `docs/TECH_JUSTIFICATION.md` | MySQL (ACID, CHECK/FK, procedures, roles), Neo4j (traversals, vector index, why not MongoDB/pgvector), FastAPI (OpenAPI → TS types, raw SQL visibility), Next.js + shadcn (rubric, SSR, middleware auth), Docker |
| `README.md` | overview, architecture diagram, setup (`.env`, compose, migrate, sync, run), demo accounts, screenshots, rubric map link |
| `docs/CONTRIBUTIONS.md` | member → owned slice (e.g., A: DB design + SQL catalogue; B: Neo4j + vector; C: FastAPI + auth/RBAC; D: Next.js + docs), with commit/PR links |
| `docs/VIVA_NOTES.md` | likely questions: why derived reviewer, generated-flag uniqueness trick, DEFINER procedures + RBAC, FOR UPDATE locking, normal forms, why a graph, how the vector index works, sync consistency |

**Git/GitHub:** a GitHub repo, `main` protected, branch per phase (`p3-applications`), PRs reviewed by a teammate, conventional commits (`feat(db): …`), tags `v0.1`…`v1.0` per phase. Commits come from each member's own account so individual contribution is visible.

---

## 12. Testing

`pytest` + `httpx` against compose MySQL and Neo4j. The fixture re-applies `db/*` + seed and runs `sync_graph --full`.

| Area | Tests |
|---|---|
| Users/skills | duplicate email 409; `Python` vs `python ` 409; upsert level (D6) |
| Projects | team + owner membership created; deadline < creation 422; Closed → Open 409; D3 blocks tasks on close |
| Applications | self-apply 422; duplicate pending 409; reapply after reject OK; non-owner decide 403; reject creates no membership; capacity 409; **two concurrent accepts at cap − 1 → exactly one wins** |
| Tasks | non-member assignment 409; due date > deadline 409; removal unassigns non-Done tasks |
| Functions | `fn_acceptance_rate` excludes Pending/Withdrawn; `fn_level_ord` ordering |
| Queries | Q4 returns only fully qualified users on seed; Q8 depth/path; Q9 returns 30 rows |
| **RBAC** | as `tt_app`: direct `UPDATE Application` → 1142; `UPDATE Project SET owner_id` → 1143; `CALL decide_application` works; member on `/admin/*` API → 403; `/admin` page redirects non-admin |
| **Neo4j** | sync idempotent (run twice, same counts); endorse → update weight → delete; endorse a non-collaborator → 409; vector search returns the expected seeded project first; related-skill CRUD admin-only |

Frontend: `tsc --noEmit`, ESLint (150-LOC rule), vitest per form spec, and a middleware unit test for role redirects.

---

## 13. Commands

```bash
cp .env.example .env && docker compose up -d db graph
# migrate + RBAC + seed: see db-migrate skill;  graph constraints + load: see neo4j-graph skill
cd api && uv run uvicorn app.main:app --reload       |  uv run pytest -q
cd web && npm run gen && npm run dev                 |  npm run lint && npx tsc --noEmit && npx vitest run
```

`docker-compose.yml` services:
- `db`: `mysql:8.0`, port 3306, healthcheck `mysqladmin ping`.
- `graph`: `neo4j:5.26`, ports 7474/7687, `NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}`, healthcheck `cypher-shell 'RETURN 1'`.
- `api`: `./api`, depends on both being healthy.

Next.js runs locally with `npm run dev`.
