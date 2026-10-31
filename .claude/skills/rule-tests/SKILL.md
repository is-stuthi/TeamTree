---
name: rule-tests
description: Run and interpret TeamTREE's pytest business-rule suite (design doc §21: users, projects, applications, teams, tasks, analytics, matching) against Docker MySQL. Use after any SQL, procedure, trigger, or endpoint change, and to verify a phase is done.
---

# rule-tests

```bash
docker compose up -d db
cd api && uv run pytest -q                       # everything
cd api && uv run pytest -q tests/test_applications.py -k concurrent   # one area / one case
```
The `fresh_db` fixture re-applies `db/*.sql` + seed per test module (see the `db-migrate` skill).

## Reading failures
| Symptom | Usually means |
|---|---|
| Expected 409/422, got 500 | New SIGNAL code not mapped in `api/app/errors.py` |
| Expected 409, got 201 | Trigger or unique flag index missing; check `SHOW TRIGGERS` and `SHOW INDEX FROM <table>` |
| Membership exists after a reject or failed accept | `decide_application` transaction or exit handler broken |
| Concurrent-accept test lets 2 through | `SELECT … FOR UPDATE` on `Project` missing or after the count. Escalate to `architect` |
| Analytics numbers off | Denominator wrong (Pending/Withdrawn must be excluded) or seed changed |

Test catalogue and the design-doc mapping: `IMPLEMENTATION.md` §9.
For long outputs, have the `sql-scout` agent summarise the failures before fixing them.
