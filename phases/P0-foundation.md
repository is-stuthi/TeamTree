# P0 — Foundation

| | |
|---|---|
| **Rubric** | 3 DDL (4), 4 NoSQL creation (4), 8 function/trigger/procedure (6, DB side), 12 RBAC in DB (DB side) |
| **Depends on** | — |
| **Agents** | `architect` reviews DDL + RBAC before merge · `builder` writes · `sql-scout` generates seed |
| **Skills** | `db-migrate`, `neo4j-graph`, `check-docker`, `scaffold` |
| **Branch** | `p0-foundation` |
| **Spec** | `IMPLEMENTATION.md` §2 (layout), §3 (schema v2), §5.3 (Cypher creation), §6.3 (RBAC), §13 (compose) |

## Goal
Both databases run in Docker with the full v2 schema, functions, triggers, procedures, views, indexes, roles and seed data. API and web skeletons boot. Generators work.

## Tasks

### Repo
- [ ] Create a GitHub repo; protect `main`; add a PR template with a rubric-row checklist.
- [ ] `.gitignore` (`.env`, `node_modules`, `.venv`, `__pycache__`, `.next`), `.env.example` with every var from the `check-docker` skill.
- [ ] `docker-compose.yml`: `db` (mysql:8.0), `graph` (neo4j:5.26), `api`, each with a healthcheck.

### MySQL (`db/`)
- [ ] `001_schema.sql`: tables exactly as in §3.1.
- [ ] `002_functions.sql`: `fn_level_ord`, `fn_is_active_member`, `fn_active_member_count`, `fn_acceptance_rate`, `fn_is_admin`.
- [ ] `003_triggers.sql`: `trg_application_bi`, `validate_task` + `trg_task_bi/bu`, `trg_project_bu`.
- [ ] `004_procedures.sql`: all procedures in §3.4. Write the full bodies now; later phases only call them.
- [ ] `005_views.sql`: the 8 views in §3.5.
- [ ] `006_indexes.sql`.
- [ ] `007_rbac.sql`: roles, grants, `tt_app`/`tt_report` users with `${…}` placeholders.
- [ ] `seed.sql` (via `sql-scout`): data per §3.7. Password hashes are bcrypt of `password123`. Demo logins: `admin@teamtree.dev`, `alice@teamtree.dev`, `bob@teamtree.dev`.
- [ ] `queries/catalogue.sql` and `queries/dml_demo.sql` with header comments only; later phases append to them.

### Neo4j (`graph/`)
- [ ] `001_constraints.cypher`, `002_vector_indexes.cypher` (§5.3).
- [ ] `003_demo_queries.cypher`: header only.

### API skeleton (`api/`)
- [ ] `pyproject.toml` (uv) with these dependencies:
  - Runtime: fastapi, uvicorn[standard], aiomysql, cryptography, neo4j, passlib[bcrypt], python-jose[cryptography], pydantic-settings, sentence-transformers.
  - Dev: pytest, pytest-asyncio, httpx.
- [ ] `app/settings.py`, `app/db.py` (pool as `tt_app`; `call_proc`, `fetch_all`, `fetch_one`), `app/graph/driver.py`, `app/errors.py` (full map from §8), `app/main.py` with `GET /health` that pings both DBs.
- [ ] `scripts/dump_openapi.py`.
- [ ] `tests/conftest.py`: `fresh_db` fixture (apply `db/*` + seed as root; app connects as `tt_app`), plus a `graph` fixture that clears Neo4j and applies `graph/001–002`.

### Web skeleton (`web/`)
- [ ] `create-next-app` + `shadcn init` + the `add` list in §7.1.
- [ ] `eslint.config.mjs` with the `max-lines` rule; `package.json` scripts `gen`, `gen:openapi`, `gen:ui`.
- [ ] `plopfile.mjs` + `plop-templates/` for router, component and page (see `scaffold/references/templates.md`).
- [ ] An empty `app/(public)/page.tsx` landing page that renders a shadcn `Card`.

## Done when
- `docker compose up -d` shows all services healthy.
- A full `db-migrate` apply runs with zero errors. `SHOW PROCEDURE STATUS`, `SHOW FUNCTION STATUS` and `SHOW TRIGGERS` list every object.
- As `tt_app`, `UPDATE Application SET status='Accepted' WHERE a_id=1` fails with **1142**, and `CALL decide_application(…)` works for the seeded owner.
- `SHOW VECTOR INDEXES` shows both indexes `ONLINE`.
- `GET /health` returns `{"mysql":"ok","neo4j":"ok"}`.
- `npx plop component Demo` produces a file that passes lint; `npm run build` succeeds.
- Tests: `test_schema.py` covers duplicate email, normalized skill duplicate, deadline CHECK, one team per project, and the generated-flag uniqueness on `Joins`/`Application`.

## Demo
Show `SHOW GRANTS FOR 'tt_app'@'%' USING 'tt_member_app'`, then the 1142 denial, then `SHOW VECTOR INDEXES` in the Neo4j Browser.
