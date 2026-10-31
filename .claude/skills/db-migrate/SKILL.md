---
name: db-migrate
description: Reset, apply, or seed the TeamTREE MySQL database in Docker, apply the RBAC roles and users, or add a new SQL migration (tables, functions, triggers, procedures, views, indexes, grants). Use whenever db/*.sql changes or the DB needs a clean state.
---

# db-migrate

Files in `db/` are applied **in filename order, as root**:
`001_schema` → `002_functions` → `003_triggers` → `004_procedures` → `005_views` → `006_indexes` → `007_rbac` → `seed`.
`001` drops and recreates every table, so a full apply is also a reset.
`db/queries/*.sql` are rubric demo files and are **not** part of the migration.

## Apply / reset
```bash
docker compose up -d db                       # MySQL is on host port $MYSQL_PORT (3307 on this machine)
cd api && .venv/Scripts/python scripts/migrate.py            # all files + seed
cd api && .venv/Scripts/python scripts/migrate.py --no-seed
cd api && .venv/Scripts/python scripts/migrate.py --only 005_views.sql
```
(`uv run python scripts/migrate.py` also works if uv is installed.)

`migrate.py` does the following:
- Handles `DELIMITER` blocks and strips full-line `--` comments. Never end a comment line with the active delimiter inside a statement.
- Substitutes `${TT_APP_PASSWORD}` / `${TT_REPORT_PASSWORD}` from `.env`, and `${SEED_PASSWORD_HASH}` with a bcrypt hash of `password123`. Every seeded login uses that password.

Procedures and functions are created **by root** because they are `SQL SECURITY DEFINER`, and that is what lets `tt_app` use them.

## Quick checks
```sql
SHOW TRIGGERS; SHOW PROCEDURE STATUS WHERE Db='teamtree'; SHOW FUNCTION STATUS WHERE Db='teamtree';
SHOW GRANTS FOR 'tt_app'@'%' USING 'tt_member_app';
```
RBAC smoke test: as `tt_app`, `UPDATE Application SET status='Accepted' WHERE a_id=1;` must fail with error 1142. `tests/test_rbac_db.py` automates this.

## Adding or changing SQL
Read `references/conventions.md` first.
Changes to keys, constraints, grants or locking go to the `architect` agent.
After any change: run a full apply, then the `rule-tests` skill. If users, skills, projects or memberships changed, also run the `neo4j-graph` full sync.
