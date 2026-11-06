# TeamTREE

**A skill-based project team formation and collaboration platform.** People list their skills,
owners post projects with skill requirements, applicants apply, owners accept them into a team
in a single transaction, and the team tracks tasks. A Neo4j graph adds collaborator networks,
endorsements and semantic (vector) project search.

DBMS Level-3 mini project (PES University). Every rubric row maps to concrete evidence in
[IMPLEMENTATION.md §0](IMPLEMENTATION.md#0-rubric-map-dbms-level-3-50-marks).

```
 Next.js 15 + shadcn ──► /api/proxy (httpOnly JWT) ──► FastAPI ──┬──► MySQL 8   (system of record:
   schema-driven forms      route guards (middleware)    raw SQL  │              procedures, triggers,
   & dashboards (JSON)                                   + Cypher │              views, roles)
                                                                  └──► Neo4j 5   (graph + vector index)
```

## Quick start

Prerequisites: Docker, Python 3.11–3.12, Node 20+. Paths below are for macOS/Linux; on Windows
use `.venv\Scripts\` instead of `.venv/bin/`.

```bash
cp .env.example .env                 # change the passwords; set MYSQL_PORT=3307 if 3306 is taken
docker compose up -d db graph        # MySQL on $MYSQL_PORT, Neo4j 7474/7687 (wait for "healthy")

cd api
python -m venv .venv
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # optional: CPU-only torch, much smaller
.venv/bin/pip install -e ".[dev,graph]"
.venv/bin/python scripts/migrate.py              # schema, functions, triggers, procedures, views, indexes, roles, seed
.venv/bin/python scripts/sync_graph.py --full    # Neo4j constraints, vector indexes, projection + graph seed
.venv/bin/python -m uvicorn app.main:app --reload    # http://localhost:8000/docs  (leave running)

# in a second terminal
cd web
cp .env.example .env.local           # JWT_SECRET must equal the one in ../.env
npm ci && npm run dev                # http://localhost:3000
```

Admins can reload the demo data at any time from **Admin → Users & roles → Reset seed data**
(development only: disabled when `APP_ENV=production` and hidden in production builds).

### Demo accounts (password `password123`)

| Email | Role | Good for showing |
|---|---|---|
| `admin@teamtree.dev` | admin | skill catalogue, roles, related-skill graph editor, all analytics |
| `alice@teamtree.dev` | member | owns *Plant Disease Classifier*: review applications, accept |
| `chitra@teamtree.dev` | member | owns *Smart Inventory Tracker*: skill gap (Docker), candidates, graph suggestions |
| `dev@teamtree.dev` | member | owns *Portfolio Generator*: 3-level task tree, team history |
| `farhan@teamtree.dev` | member | collaboration network, recommendations |
| `jay@teamtree.dev` | member | the only fully qualified candidate for Chitra's project |

## Features

- **Profiles & skills:** proficiency per skill, admin-managed catalogue (case-insensitive unique).
- **Projects:** requirements per skill and role, domains, capacity, lifecycle; browse and filter.
- **Applications:** apply, withdraw, accept or reject. Accepting is one transaction that stays capacity-safe under concurrency.
- **Teams & tasks:** membership history, removal with task unassignment, ownership transfer, subtask tree.
- **Matching:** transparent weighted score (coverage 50 / proficiency 20 / experience 15 / domain 10 / availability 5) and a skill-gap report.
- **Graph (Neo4j):** collaborator network, recommended collaborators, shortest path, related skills, endorsements, vector search and similar projects or people.
- **Analytics:** skills demand vs supply, projects, applications (acceptance rate excludes pending and withdrawn), users and teams (admin).
- **Security in three layers:** Next.js middleware, FastAPI role checks, and **MySQL roles and grants**. The app's DB user cannot write applications or memberships except through stored procedures.

## Screenshots

| | |
|---|---|
| ![Browse projects](docs/screenshots/02-browse-projects.png) **Browse & filter projects** | ![Review applications](docs/screenshots/04-applications-review.png) **Owner reviews applications** |
| ![Candidates](docs/screenshots/05-candidates.png) **Weighted candidate scores** | ![Skill gap](docs/screenshots/06-skill-gap.png) **Skill-gap dashboard** |
| ![Task tree](docs/screenshots/07-task-tree.png) **Subtask tree (recursive CTE)** | ![Network](docs/screenshots/08-network-graph.png) **Neo4j collaboration network** |
| ![Semantic search](docs/screenshots/09-semantic-search.png) **Vector search** | ![Analytics](docs/screenshots/10-analytics.png) **Analytics (views as `tt_report`)** |

More in [`docs/screenshots/`](docs/screenshots/). Captured against the seed data.

## Where the DBMS work is

| What | Where |
|---|---|
| DDL with constraints | [`db/001_schema.sql`](db/001_schema.sql) |
| Functions / triggers / procedures | [`db/002_functions.sql`](db/002_functions.sql), [`003_triggers.sql`](db/003_triggers.sql), [`004_procedures.sql`](db/004_procedures.sql) |
| Views (incl. CTE + window) / indexes | [`db/005_views.sql`](db/005_views.sql), [`006_indexes.sql`](db/006_indexes.sql), [EXPLAIN evidence](docs/explain.md) |
| RBAC in the database | [`db/007_rbac.sql`](db/007_rbac.sql) |
| Query catalogue Q1–Q12 (join, nested, correlated, recursive, window, self-join, union) | [`db/queries/catalogue.sql`](db/queries/catalogue.sql) |
| DML demo D1–D7 | [`db/queries/dml_demo.sql`](db/queries/dml_demo.sql) |
| Neo4j creation / demo queries (R/U/D + vector) | [`graph/`](graph/) |
| ER diagram (Chen + crow's foot) / relational schema / tech choices | [`docs/ER Diagram.png`](docs/ER%20Diagram.png), [`docs/er.svg`](docs/er.svg), [`docs/RELATIONAL_SCHEMA.md`](docs/RELATIONAL_SCHEMA.md), [`docs/TECH_JUSTIFICATION.md`](docs/TECH_JUSTIFICATION.md) |

## Tests

```bash
cd api && .venv/bin/python -m pytest -q          # business rules, RBAC, concurrency, graph, analytics, Q1–Q12/D1–D7 smoke
cd web && npm run lint && npm run typecheck && npm test && npm run build
```

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs all of this against fresh MySQL and Neo4j containers.

## Project docs

[Design document](docs/TeamTREE_Design_Document.md) · [Implementation plan](IMPLEMENTATION.md) ·
[Build phases](phases/README.md) · [Viva notes](docs/VIVA_NOTES.md) · [Contributions](docs/CONTRIBUTIONS.md)
