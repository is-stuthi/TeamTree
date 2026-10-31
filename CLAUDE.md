# TeamTREE

A skill-based team formation platform (DBMS lab project). The full plan is in `IMPLEMENTATION.md` and the rationale is in `docs/TeamTREE_Design_Document.md`.
Open those only when a task needs them.

## Stack
MySQL 8 (`db/*.sql`: procedures, triggers, views) · FastAPI with raw SQL (`api/`) · Vite + React + TS + shadcn/ui (`web/`) · Docker Compose.

## Hard rules
- **API contract = `web/src/api/schema.d.ts` + `ui-schemas.d.ts`.** Read these, not `api/app/**`, unless you are changing backend behaviour. Never hand-edit them; regenerate with the `gen-types` skill.
- **Schema-driven UI:** a form or dashboard is a JSON spec in `web/src/specs/` rendered by `SchemaForm` / `SchemaDashboard`. Write JSON, not JSX (`schema-form` skill).
- **≤ 150 lines** per custom source file (ESLint `max-lines`). Split before you exceed it (`scaffold` skill).
- **shadcn only** for UI primitives: `npx shadcn@latest add <x>`. Don't edit `components/ui/` by hand.
- **Generators for boilerplate:** `npx plop router|component|page`, the shadcn CLI and the type generators.
- Business rules live in the DB (procedures and triggers that use `SIGNAL '45000'`). Map new SIGNAL messages in `api/app/errors.py`.
- Never use ON DELETE CASCADE to Users or Project; they are soft-deleted.

## Model routing (subagents in `.claude/agents/`)
- `sql-scout` (Haiku): simple questions, log/test summaries, basic SQL, seed data, simple JSON specs.
- `builder` (Sonnet): features, routine edits, standard debugging, generators, tests.
- `architect` (Opus): schema/transaction/locking design, concurrency or infra failures, big refactors. Plans only.

## Skills (`.claude/skills/`, loaded on demand)
- `db-migrate`: reset, apply, seed DB; add a migration.
- `gen-types`: regenerate the TS defs from OpenAPI and UI schemas.
- `scaffold`: plop + shadcn generators; splitting large files.
- `schema-form`: add or change forms and dashboards via JSON specs.
- `check-docker`: diagnose compose, MySQL health, env and ports.
- `rule-tests`: run and interpret the business-rule pytest suite.

## Commands
```
docker compose up -d db
cd api && uv run uvicorn app.main:app --reload    |  uv run pytest -q
cd web && npm run gen && npm run dev              |  npm run lint && npx tsc --noEmit
```
