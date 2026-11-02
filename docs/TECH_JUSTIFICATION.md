# TeamTREE: Technology justification

| Layer | Choice | Why this, for this project |
|---|---|---|
| Relational DB | **MySQL 8.0** (InnoDB) | ACID transactions with row locks for the accept workflow; CHECK constraints (8.0.16+), generated columns, recursive CTEs and window functions (8.0); stored procedures, functions and triggers; **roles** (`CREATE ROLE`) for database-level RBAC. Everything the rubric's SQL rows ask for, in one well-known engine. |
| NoSQL / Vector | **Neo4j 5.26** | The questions that matter here are *multi-hop*: collaborators of collaborators, shortest collaboration path, skills related to a missing skill. These are one-line Cypher patterns but awkward recursive self-joins in SQL. Neo4j 5 also has **native vector indexes** (cosine, HNSW), so semantic project search needs no second datastore. |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Free, offline, CPU-friendly, 384 dimensions. No paid API keys needed for a lab demo. |
| Backend | **FastAPI** (Python, raw SQL + Cypher, no ORM) | Raw SQL keeps the DBMS logic visible for evaluation (procedures, views, labelled queries). Pydantic models are the single source of truth for validation and generate **OpenAPI**, which we turn into TypeScript types. Async drivers for both databases. |
| Frontend | **Next.js 15** (App Router) + **shadcn/ui** | Required by the rubric. Server Components fetch data server-side with the session token; `middleware.ts` gives route-level auth; shadcn provides accessible, consistent primitives without a heavy UI framework. |
| UI architecture | Schema-driven forms & dashboards | Forms and dashboards are JSON specs rendered by two static components, so new screens are data, not code. Validation rules come from the same Pydantic models the API enforces. |
| Auth | JWT (HS256) in an **httpOnly** cookie | The token never reaches browser JavaScript; a same-origin proxy attaches it. The API re-reads role and `is_active` on every request, so role changes and deactivation take effect immediately. |
| Infra | Docker Compose | One command brings up MySQL and Neo4j identically on every teammate's machine and in CI. |
| Quality | pytest, vitest, ESLint (150-line rule), GitHub Actions | The business rules (§12, §21) are executable tests, including a deterministic concurrency test of the accept transaction. |

## Alternatives considered

| Instead of | Considered | Why not |
|---|---|---|
| Neo4j | MongoDB | Document store: good for flexible profiles, but no native graph traversal; collaborator paths would need application-side BFS. |
| Neo4j vector | pgvector / a separate vector DB | Would add PostgreSQL alongside MySQL (or a third store) just for similarity; Neo4j already holds the projects and people being compared. |
| MySQL | PostgreSQL | Equally capable; MySQL matched the course material and the team's existing `schema.sql`. |
| Raw SQL | SQLAlchemy ORM | An ORM would hide the SQL the rubric evaluates (joins, subqueries, procedure calls). |
| FastAPI | Next.js route handlers only | Fewer services, but blurs the frontend/backend split the rubric scores separately and loses the OpenAPI → TS pipeline. |

## Consistency between the two databases

MySQL is the **system of record**. Neo4j holds (a) a projection of MySQL rows (users, skills,
projects, memberships, collaboration pairs from the Q11 self-join) and (b) graph-only data that
exists nowhere else: endorsements, curated skill relations, embeddings.

After each MySQL commit the API updates the graph with idempotent `MERGE`s. A Neo4j failure is
logged and never rolls back MySQL; `python scripts/sync_graph.py` reconciles. The trade-off is
eventual consistency for the graph, in exchange for MySQL features keeping working when Neo4j is down.
Tests cover this (`test_neo4j_down_does_not_block_mysql`).
