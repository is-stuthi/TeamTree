# Viva notes

## 5-minute demo script (in rubric order)

1. **ER & schema (rows 1–3):** `docs/er.svg` and the Chen diagram. In `db/001_schema.sql` point at
   `uq_joins_active` + `active_flag` (history with one active row) and `chk_application_decision`.
2. **DML (row 6):** run D2 (INSERT … SELECT) and D3 (UPDATE … JOIN) from `db/queries/dml_demo.sql`.
3. **Queries (row 7):** Q4 (NOT EXISTS relational division), Q5 (correlated), Q8 (recursive CTE tree)
   from `db/queries/catalogue.sql`, side by side with the UI pages that use them.
4. **Procedure / trigger / CTE (row 8):** try to apply to a full project (`PROJECT_FULL` from the
   trigger). Walk through `decide_application` (row locks, `FOR SHARE` count, exit handler + RESIGNAL).
5. **RBAC (row 12):** `SHOW GRANTS FOR 'tt_app'@'%' USING 'tt_member_app';` then as `tt_app`:
   `UPDATE Application SET status='Accepted' WHERE a_id=1;` → error **1142**. Log in as a member,
   open `/admin` → redirected. Promote them as admin → the Admin link appears without re-login.
6. **Neo4j (rows 4, 9):** Neo4j Browser → `graph/003_demo_queries.cypher`: network, shortest path,
   vector similarity, then endorse → change weight → delete. In the app: `/graph/network`,
   `/graph/search?q=machine learning image classifier`.
7. **Next.js (row 10):** owner flow: review applications → accept → team → tasks tree → skill gap.

## Likely questions

**Why isn't the reviewer stored on Application?**
It's determined by `p_id → Project.owner_id`. Storing it adds a transitive dependency (3NF
violation) and an update anomaly on ownership transfer.

**How do you allow rejoining a team but prevent duplicate active membership?**
`active_flag = IF(leave_date IS NULL, 1, NULL)` (stored generated column) inside
`UNIQUE(t_id, u_id, active_flag)`. UNIQUE ignores NULLs, so past rows don't collide; only one row can
have flag 1. The same trick gives "one *pending* application per user and project".

**How is accepting an application atomic, and why can't two owners overfill a team?**
`decide_application` runs in one transaction with an EXIT HANDLER that rolls back and re-raises.
It locks the Project row (`FOR UPDATE`) first, then counts members with `FOR SHARE`, a locking read
that sees rows committed by a concurrent accept. A plain `SELECT` would read the REPEATABLE READ
snapshot taken earlier in the transaction and could undercount; `tests/test_concurrency.py`
demonstrates this (it fails if the count is changed to a plain SELECT).

**Why procedures with SQL SECURITY DEFINER?**
The app's DB user (`tt_app`) has no write privilege on Application, Joins, Team or Skill. The procedures
run with root's privileges but check the acting user themselves. That makes them the only path to
those writes, so the rules can't be bypassed even with a SQL injection in the app.

**What do the triggers do, and why not do it in the API?**
They validate only (never write other rows): application to Open projects, not your own, not when full;
task assignee must be an active member; due date ≤ deadline; no reopening finished projects. Being in
the DB, they hold for every client (API, admin console, scripts).

**Normal forms?**
All tables are in BCNF: every determinant is a candidate key. Derived values (age, overdue, team size,
acceptance rate, skill gap) are views, not columns. See `docs/RELATIONAL_SCHEMA.md` §3.

**Why a graph database at all?**
Multi-hop questions (collaborators of collaborators, shortest path, related skills) are natural
traversals in Cypher and awkward recursive joins in SQL. Neo4j's vector index also gives semantic
search without another datastore.

**How does the vector search work?**
Each project's name, description, domains and required skills are embedded into a 384-dimensional
vector (MiniLM). `CREATE VECTOR INDEX … cosine` builds an approximate-nearest-neighbour index;
`db.index.vector.queryNodes` returns the closest projects to the embedded query text.

**What if Neo4j is down?**
MySQL is the system of record; graph sync runs after the MySQL commit, and failures are logged, never
raised. MySQL features keep working; `scripts/sync_graph.py` reconciles. There's a test for exactly this.

**How is the match score computed? Is it "AI"?**
No ML. It's a transparent weighted sum: coverage 50, proficiency 20 (capped at the required level),
experience 15, domain 10, availability 5. The UI shows the per-factor breakdown and labels it "indicative".

**Acceptance rate denominator?**
Accepted / (Accepted + Rejected). Pending and Withdrawn are excluded (`fn_acceptance_rate`).

## Modification drills (practise each once)

| Ask | Where | Sketch |
|---|---|---|
| Add a column with a CHECK | `db/001_schema.sql` | e.g. `Users.github_url VARCHAR(200) NULL, CHECK (github_url IS NULL OR github_url LIKE 'https://github.com/%')`; re-run `migrate.py`; add to `ProfilePatch` and the column grant in `007_rbac.sql` |
| Add a trigger | `db/003_triggers.sql` | e.g. block a task title longer than its parent's project allows; `SIGNAL SQLSTATE '45000'` + map the code in `api/app/errors.py` |
| Add a form field | `api/app/models/*.py` + `api/app/ui_schemas/*` | the field appears in the UI automatically (schema-driven); run `npm run gen` |
| Add a Cypher query | `api/app/queries/graph.py` + a route in `routers/graph.py` | parameterised, read-only |
| New analytics chart | `web/specs/dashboards/*.json` | JSON only; no React changes |
