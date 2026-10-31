# P3 — Applications & the accept transaction

| | |
|---|---|
| **Rubric** | 6 DML (4), 8 procedure/trigger (6) |
| **Depends on** | P2 |
| **Agents** | `builder` · `architect` reviews locking and the concurrency test before merge |
| **Skills** | `scaffold`, `schema-form`, `rule-tests`, `db-migrate` (if a procedure needs a fix) |
| **Branch** | `p3-applications` |
| **Spec** | `IMPLEMENTATION.md` §3.3 (`trg_application_bi`), §3.4 (`decide_application` etc.), design doc §9.4–9.5, §13.1–13.7, §16.1–16.2 |

## Goal
Users apply to Open projects and can withdraw. Owners accept or reject. Accepting updates the application and creates the membership atomically, and capacity holds even under concurrent accepts.

## Tasks

### API (`plop router applications`)
- [ ] `POST /projects/{id}/applications` → `CALL apply_to_project`. Map the duplicate key on `uq_application_pending` → 409 `DUPLICATE_PENDING`.
- [ ] `GET /projects/{id}/applications?status=` (owner only; join applicant profile + skills).
- [ ] `GET /users/me/applications`.
- [ ] `POST /applications/{id}/decision` `{decision, role}` → `CALL decide_application`.
- [ ] `POST /applications/{id}/withdraw` → `CALL withdraw_application`.
- [ ] After a successful accept, call sync `upsert_membership(p_id)` (a stub until P6).
- [ ] UI schema `application_create` (message min 20 characters), `decision` (role text).

### Web
- [ ] `/projects/[id]`: Apply button → `Dialog` + `SchemaForm`. Hide it for the owner, existing members and non-Open projects; show "Pending" when the user has already applied.
- [ ] `/projects/[id]/manage/applications`: `Tabs` by status; an applicant row with skills and Accept/Reject buttons (Accept opens a role field); optimistic update + toast.
- [ ] `/dashboard/applications`: my applications with status `Badge` and a Withdraw action.

### Tests (`test_applications.py`)
- [ ] Valid apply → Pending.
- [ ] Self-apply → 422 `SELF_APPLICATION`.
- [ ] Duplicate pending → 409; reapply after Rejected or Withdrawn → 201.
- [ ] Apply to an Ongoing/Closed project → 409 `PROJECT_NOT_OPEN`; apply at capacity → 409 `PROJECT_FULL`.
- [ ] Non-owner decide → 403; deciding a non-Pending application → 409.
- [ ] Reject → no `Joins` row; accept → `Joins` row + `decision_date` set.
- [ ] Withdraw by a non-applicant → 403.
- [ ] **Concurrency:** with capacity = members + 1, fire two accepts with `asyncio.gather` on separate connections. Exactly one succeeds and the other gets `PROJECT_FULL`.
- [ ] **Rollback:** force a membership insert failure (pre-insert an active `Joins` row for the applicant). The application stays Pending.

## Done when
The full apply → review → team flow works in the UI, the concurrency and rollback tests are green, and the architect has signed off on the locking. The gate passes.

## Demo
Two browser windows accept the last slot at the same moment: one succeeds. Then walk through `decide_application` in `004_procedures.sql`: `FOR UPDATE` lock order, the exit handler and `RESIGNAL`.
