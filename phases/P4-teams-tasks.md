# P4 — Teams, tasks & ownership transfer

| | |
|---|---|
| **Rubric** | 7 queries (4: recursive, correlated), 8 trigger/procedure/CTE (6) |
| **Depends on** | P3 |
| **Agents** | `builder` |
| **Skills** | `scaffold`, `schema-form`, `rule-tests` |
| **Branch** | `p4-teams-tasks` |
| **Spec** | `IMPLEMENTATION.md` §3.3 (`validate_task`), §3.4 (`assign_task`, `remove_member`, `leave_team`, `transfer_ownership`), §4.2 Q5/Q8, design doc §9.6–9.7, §13.8–13.10, §16.3–16.4 |

## Goal
Owners and members manage the team and its tasks, including subtasks. Membership history is preserved. Removed members' open tasks are unassigned. Ownership can be transferred.

## Tasks

### API
- [ ] `plop router teams`:
  - `GET /projects/{id}/team?include_past=` (`TeamMemberDetails`).
  - `DELETE /projects/{id}/team/{user_id}` → `remove_member`.
  - `POST /projects/{id}/team/leave` → `leave_team`.
  - `GET /users/me/teams`.
- [ ] `POST /projects/{id}/transfer` `{new_owner}` → `transfer_ownership`.
- [ ] `plop router tasks`:
  - `GET/POST /projects/{id}/tasks` (owner or active member; `parent_task_id` optional).
  - `PATCH /tasks/{id}` (status, priority, due date).
  - `POST /tasks/{id}/assign` → `assign_task`.
  - `GET /projects/{id}/tasks/tree` → **Q8** recursive CTE.
  - `GET /users/me/tasks`.
- [ ] `GET /projects/{id}/team/top-contributors` → **Q5** (correlated).
- [ ] Sync stubs: `deactivate_membership`, an owner change in `upsert_project`.
- [ ] UI schemas `task_create`, `task_edit`, `transfer_ownership`.

### Web
- [ ] `/projects/[id]/manage/team`: active and past members `Table`, Remove (confirm `Dialog` that warns how many tasks will be unassigned), Transfer ownership.
- [ ] `/projects/[id]/manage/tasks`: a tree view built from Q8 (indent by `depth`), status `Select` inline, assign `Select` that lists only active members, and a create-task `Dialog`.
- [ ] `/dashboard/teams` and `/dashboard/tasks` (grouped by project, overdue highlighted).

### SQL catalogue
- [ ] Append **Q5** and **Q8** with labels.

### Tests (`test_teams_tasks.py`)
- [ ] Assign to a non-member → 409 `ASSIGNEE_NOT_MEMBER`.
- [ ] Due date after the project deadline → 409.
- [ ] Remove a member → `leave_date` set, row kept, their non-Done tasks have `u_id` NULL and Done tasks are untouched.
- [ ] A removed member can be re-added through a new application, giving a second `Joins` row (history).
- [ ] The owner can't be removed and can't leave without transferring.
- [ ] Transfer to a non-member → 409; a successful transfer swaps roles and writes `Ownership_Transfer`.
- [ ] Q8 returns correct `depth`/`path` for the seeded 3-level tree; Q5 matches a hand-computed seed answer.

## Done when
The task tree renders, assignment rules hold, and member removal and transfer behave as specified. The gate passes.

## Demo
1. Remove a member: their tasks show as unassigned, and `TeamMemberDetails` still lists them as past.
2. Run Q8 in MySQL Workbench next to the UI tree.
