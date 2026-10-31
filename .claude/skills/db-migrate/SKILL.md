---
name: db-migrate
description: Reset, apply, or seed the TeamTREE MySQL database in Docker, or add a new SQL migration (tables, triggers, procedures, views, indexes). Use whenever db/*.sql changes or the DB needs a clean state.
---

# db-migrate

The SQL files in `db/` are applied **in filename order**:
`001_schema` → `002_triggers` → `003_procedures` → `004_views` → `005_indexes` → `seed`.
`001` drops and recreates every table, so a full apply is also a reset.

## Apply / reset
```bash
docker compose up -d db
for f in db/0*.sql db/seed.sql; do
  docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" teamtree' < "$f" || { echo "FAILED: $f"; break; }
done
```
`001` creates the `teamtree` database itself. On the very first run, apply it without the trailing `teamtree` database argument.

## Quick checks
```sql
SHOW TABLES; SHOW TRIGGERS; SHOW PROCEDURE STATUS WHERE Db='teamtree';
SELECT TABLE_NAME FROM information_schema.VIEWS WHERE TABLE_SCHEMA='teamtree';
```

## Adding or changing SQL
Read `references/conventions.md` before editing any procedure or trigger.
Changes to keys, constraints or locking go to the `architect` agent first.
After changing SQL: run a full apply, then the `rule-tests` skill.
