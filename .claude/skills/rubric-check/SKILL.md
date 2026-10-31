---
name: rubric-check
description: Audit TeamTREE against the PES DBMS Level-3 rubric (50 marks). Walks the IMPLEMENTATION.md §0 rubric map, verifies each deliverable exists and is demonstrable, and produces a gap list and a viva checklist. Use before each phase demo, before submission, or when asked "are we covering the rubric?".
---

# rubric-check

1. Read `IMPLEMENTATION.md` §0 (rubric map) only.
2. For each row, check the evidence and mark it ✅ done, 🟡 partial or ❌ missing:

| # | Check |
|---|---|
| 1 ER (2) | `docs/ER Diagram.png` + `docs/er.mmd` exist and show the v2 changes (role, max_team_size, leave_date, Withdrawn, Ownership_Transfer) |
| 2 Schema (3) | `docs/RELATIONAL_SCHEMA.md` lists PK/FK/UNIQUE/CHECK + FDs + normal-form argument for every table in `db/001_schema.sql` |
| 3 DDL (4) | `db/001_schema.sql` applies cleanly (`db-migrate`) |
| 4 NoSQL create (4) | `graph/001`, `graph/002` apply; `SHOW VECTOR INDEXES` is ONLINE; `sync_graph --full` loads data |
| 5 Tech (1) | `docs/TECH_JUSTIFICATION.md` covers MySQL, Neo4j, FastAPI and Next.js, and the alternatives considered |
| 6 DML (4) | `db/queries/dml_demo.sql` D1–D7 present and each runs |
| 7 Queries (4) | `db/queries/catalogue.sql` Q1–Q12 labelled; at least one each of nested, correlated, recursive and join; each wired to an endpoint |
| 8 Adv SQL (6) | at least one each of function, procedure, trigger and CTE exists and is exercised by a test |
| 9 NoSQL RUD (7) | `/graph/*` has working Read (incl. a vector search), Update and Delete endpoints, each reachable from a Next.js page |
| 10 Next.js (3) | `web/` builds (`npm run build`); every route in §7.2 renders |
| 11 API (2) | FastAPI hits both MySQL and Neo4j; `/docs` OpenAPI loads |
| 12 Auth (4) | login/register UI; admin vs member enforced in middleware, API and **MySQL grants** (`tests/test_rbac.py` green) |
| 13 Docs/Git (2) | README setup works from scratch; GitHub repo has PRs per phase |
| 14 Originality (4) | `docs/CONTRIBUTIONS.md` and `docs/VIVA_NOTES.md` exist; commits come from each member |

3. Use `Glob`/`Grep` for existence checks and the `rule-tests` skill for behaviour. Have the `sql-scout` agent do the bulk file checks.
4. Output a table (row, status, evidence path, fix needed) and the estimated score using the rubric's partial-credit column. Then list a 5-minute **viva demo script** in rubric order: ER → DDL → DML → queries → procedure/trigger/CTE → RBAC denial demo → Neo4j browser + vector search → Next.js walkthrough.
