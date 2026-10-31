# TeamTREE

A skill-based team formation platform (PES DBMS Level-3 mini project, graded on a 50-mark rubric).
- Plan and rubric map: `IMPLEMENTATION.md` §0. Rationale: `docs/TeamTREE_Design_Document.md`. Read only the section a task needs.
- **Build work is organised by phase:** `phases/README.md` is the index and shared gate. Load only the current `phases/P<N>-*.md`.

## Stack
- MySQL 8 (`db/*.sql`: functions, triggers, procedures, views, RBAC roles)
- Neo4j 5 (`graph/*.cypher`: graph + vector indexes)
- FastAPI with raw SQL + Cypher (`api/`)
- Next.js 15 App Router + TS + shadcn/ui (`web/`)
- Docker Compose

## Hard rules
- **API contract = `web/lib/api/schema.d.ts` + `ui-schemas.d.ts`.** Read these, not `api/app/**`, unless you are changing backend behaviour. They are generated; use the `gen-types` skill.
- **Schema-driven UI:** forms and dashboards are JSON specs (`web/specs/` or `api/app/ui_schemas/`) rendered by `SchemaForm` / `SchemaDashboard`. Write JSON, not JSX (`schema-form` skill).
- **≤ 150 lines** per custom source file. Split early (`scaffold` skill).
- **shadcn only** for primitives (`npx shadcn@latest add <x>`); never hand-edit `components/ui/`.
- **Generators** for boilerplate: plop (router, component, page), shadcn CLI, type generators.
- Business rules live in MySQL (procedures/triggers, `SIGNAL '45000'`). Map new codes in `api/app/errors.py`.
- The API connects as low-privilege `tt_app`. Guarded writes (Application, Joins, Skill, roles) go **only** through DEFINER procedures. Never grant around this.
- MySQL is the system of record. Neo4j holds a projection plus graph-only data (endorsements, RELATED_TO, embeddings).
- No ON DELETE CASCADE to Users or Project (soft delete).
- Every feature must map to a rubric row; check with the `rubric-check` skill.

## Model routing (`.claude/agents/`)
- `sql-scout` (Haiku): simple questions, log/test summaries, basic SQL/Cypher, seed data, simple specs.
- `builder` (Sonnet): features, edits, standard debugging, generators, tests.
- `architect` (Opus): schema/RBAC/transactions/locking, MySQL ↔ Neo4j consistency, hard failures. Plans only.

## Skills (`.claude/skills/`, loaded on demand)
- `db-migrate`: MySQL apply, reset, seed, RBAC.
- `neo4j-graph`: constraints, vector indexes, sync, Cypher.
- `gen-types`: regenerate the TS defs.
- `scaffold`: plop/shadcn generators; split files.
- `schema-form`: JSON form/dashboard specs.
- `check-docker`: compose, MySQL and Neo4j health.
- `rule-tests`: pytest suite.
- `rubric-check`: verify the rubric evidence and viva readiness.

## Commands
```
docker compose up -d db graph                     # MySQL on host port $MYSQL_PORT (3307 here), Neo4j 7474/7687
cd api && .venv/Scripts/python scripts/migrate.py  |  .venv/Scripts/python scripts/graph_init.py
cd api && .venv/Scripts/python -m uvicorn app.main:app --reload   |  .venv/Scripts/python -m pytest -q
cd api && .venv/Scripts/python scripts/dump_openapi.py && cd ../web && npm run gen
cd web && npm run dev                             |  npm run lint && npm run typecheck && npm test
```
Seeded logins: `admin@teamtree.dev` (admin), `alice@`/`bob@teamtree.dev` (members), all `password123`.
