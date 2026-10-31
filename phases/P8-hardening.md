# P8 — Hardening, CI & polish

| | |
|---|---|
| **Rubric** | All rows: makes every earlier mark reliably demonstrable |
| **Depends on** | P7 |
| **Agents** | `builder` · `sql-scout` summarises test runs and LOC audits |
| **Skills** | `rule-tests`, `code-review`, `simplify`, `check-docker`, `run` |
| **Branch** | `p8-hardening` |
| **Spec** | `IMPLEMENTATION.md` §12 (full test matrix), design doc §21 |

## Goal
The whole suite is green from a clean clone. CI enforces it. The UI handles errors and empty states gracefully, and the app survives a live viva.

## Tasks

### Tests & CI
- [ ] Cross-check `IMPLEMENTATION.md` §12 against `api/tests/`, and add any missing case.
- [ ] Add an `api/tests/test_queries.py` and `test_functions.py` smoke test for every catalogue query Q1–Q12, DML D1–D7 and stored function.
- [ ] GitHub Actions `.github/workflows/ci.yml`:
  - `services: mysql:8.0, neo4j:5.26`.
  - Steps: apply `db/*` + `graph/*` → `uv run pytest -q` → `npm ci && npm run gen && git diff --exit-code lib/api/ && npm run lint && npx tsc --noEmit && npx vitest run && npm run build`.
- [ ] Cache the sentence-transformers model in CI (or mock `embed.py` behind an env flag in CI only).

### Quality
- [ ] `code-review` on the full `main...HEAD` diff, then `simplify`.
- [ ] LOC audit: `sql-scout` lists any `.py`/`.ts`/`.tsx` over 150 lines; split them with the `scaffold` skill.
- [ ] Indexes: capture `EXPLAIN` for Browse (Q-filter), Q1, Q4 and the application list before and after `006_indexes.sql`, and save it to `docs/explain.md` for the viva.
- [ ] Remove dead code, TODOs and console logs.

### UX polish
- [ ] A `loading.tsx` skeleton on every route; empty states on every table; `error.tsx` boundaries.
- [ ] Every 4xx error code has a human message in one map (`lib/errors.ts`), shown as a toast.
- [ ] Mobile pass at 375 px; keyboard navigation through forms and dialogs.
- [ ] Seed reset button on the admin page (dev only) that calls a guarded `/admin/dev/reset` endpoint and is disabled in production.

### Resilience
- [ ] `run` skill: a fresh clone → `.env` → compose → migrate → sync → dev servers, following the README steps exactly. Fix every snag.
- [ ] Stop Neo4j while the app runs: MySQL features keep working, graph pages show a friendly "graph unavailable" message.

## Done when
CI is green on `main`, a clean-clone setup takes under 10 minutes following the README, and no file is over 150 lines. The gate passes.
