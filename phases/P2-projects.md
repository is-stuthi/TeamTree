# P2 — Projects, requirements & discovery

| | |
|---|---|
| **Rubric** | 6 DML (4), 7 queries (4) |
| **Depends on** | P1 |
| **Agents** | `builder` |
| **Skills** | `scaffold`, `schema-form`, `gen-types`, `rule-tests` |
| **Branch** | `p2-projects` |
| **Spec** | `IMPLEMENTATION.md` §3.4 (`create_project`), §4.1 D2/D3, §4.2 Q1/Q6, §7.2 routes |

## Goal
Owners create and edit projects with domains and skill requirements. Everyone can browse and filter Open projects and see a project's detail page. Members get SQL-based project recommendations.

## Tasks

### API (`plop router projects`)
- [ ] `POST /projects` → `CALL create_project` (creates the project, its team and the owner's membership), then insert domains.
- [ ] `GET /projects?status=&domain=&skill=&deadline_before=&q=` over the `OpenProjects` view (with a status override for owners).
- [ ] `GET /projects/{id}`: **Q1** (5-table JOIN), plus requirements from `ProjectSkillRequirements`.
- [ ] `PATCH /projects/{id}` (owner; column-granted fields only). When the status changes to `Closed`, run **D3** (UPDATE…JOIN that marks open tasks Blocked). `PROJECT_REOPEN_FORBIDDEN` → 409.
- [ ] `PUT/DELETE /projects/{id}/requirements[/{s_id}/{role}]` and `POST /projects/{id}/requirements/copy-from/{src}` (**D2** INSERT…SELECT).
- [ ] `GET /users/me/projects` (owned + member).
- [ ] `GET /users/me/recommended-projects`: **Q6** (correlated EXISTS).
- [ ] UI schemas: `project_create`, `project_edit`, `requirement_add`, `project_filter`.
- [ ] Sync stub: `upsert_project` (embedding stays `None` until P6).

### Web
- [ ] `/projects`: filter `SchemaForm` (client-only spec in `specs/forms/project_filter.json`), `ProjectCard` grid, URL-synced filters.
- [ ] `/projects/[id]`: header, domains (`Badge`), requirements `Table`, owner card, overdue badge. Leave an Apply button placeholder for P3.
- [ ] `/dashboard/projects`: owned and member tabs; a "New project" `Dialog` with `SchemaForm`.
- [ ] `/projects/[id]/manage/requirements`: requirement table + add form + "copy from project".
- [ ] Dashboard home: a "Recommended for you" list (Q6).

### SQL catalogue
- [ ] Append **Q1** and **Q6** to `catalogue.sql`, and **D2** and **D3** to `dml_demo.sql`, with labels.

### Tests (`test_projects.py`)
- [ ] Create → Team + owner `Joins` row (role `Owner`) exist.
- [ ] Deadline before creation → 422.
- [ ] Non-owner PATCH → 403.
- [ ] Changing `owner_id` through PATCH is impossible (1143 → 403).
- [ ] Close → open tasks become Blocked (D3); Closed → Open → 409.
- [ ] Copying requirements (D2) duplicates the rows.
- [ ] Q6 returns only Open projects where the user meets at least one requirement.

## Done when
An owner can create a project with requirements, find it in Browse, and open its detail page. The gate passes.

## Demo
Create a project, then show the `Team` and `Joins` rows that the procedure created in the same transaction. Run Q1 and Q6 from `catalogue.sql` next to the UI.
