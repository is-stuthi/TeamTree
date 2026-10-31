---
name: rule-tests
description: Run and interpret TeamTREE's pytest suite (business rules from design doc §21, SQL functions and queries, MySQL RBAC, Neo4j graph and vector features) against Docker MySQL and Neo4j. Use after any SQL, Cypher, procedure, trigger, grant, or endpoint change, and to verify a phase is done.
---

# rule-tests

```bash
docker compose up -d db graph
cd api && uv run pytest -q                                   # everything
cd api && uv run pytest -q tests/test_rbac.py                # one area
cd api && uv run pytest -q tests/test_applications.py -k concurrent
```
The `fresh_db` fixture re-applies `db/*.sql` + seed (`db-migrate`) and runs `sync_graph --full` (`neo4j-graph`) once per module.

## Reading failures
| Symptom | Usually means |
|---|---|
| Expected 409/422, got 500 | New SIGNAL code not mapped in `api/app/errors.py` |
| Expected 409, got 201 | Trigger or unique flag index missing (`SHOW TRIGGERS`, `SHOW INDEX FROM …`) |
| Membership exists after a reject or failed accept | `decide_application` transaction or exit handler broken |
| Concurrent-accept test lets 2 through | `FOR UPDATE` on `Project` missing or after the count. Escalate to `architect` |
| RBAC test: direct UPDATE *succeeded* | A grant in `007_rbac.sql` is too broad, or tests connect as root instead of `tt_app` |
| Procedure fails with 1142 for `tt_app` | Procedure was created by a non-root definer, or `SQL SECURITY INVOKER` slipped in |
| Graph counts differ after a second sync | A `CREATE` was used where `MERGE` is needed (`neo4j-graph` skill) |
| Vector search returns nothing | Index not `ONLINE` yet, embeddings missing, or dimension ≠ 384 |
| Analytics numbers off | Wrong denominator (exclude Pending/Withdrawn) or seed changed |

Test catalogue: `IMPLEMENTATION.md` §12. For long outputs, have the `sql-scout` agent summarise the failures first.
