# P6 — Neo4j graph & vector search

| | |
|---|---|
| **Rubric** | 4 NoSQL/Vector creation (4), 9 NoSQL/Vector RUD (7). Together that's 11 of 50 marks, the largest single phase |
| **Depends on** | P1 (can run in parallel with P2–P5; full value after P4) |
| **Agents** | `builder` · `architect` reviews sync consistency · `sql-scout` for simple Cypher reads |
| **Skills** | `neo4j-graph`, `scaffold`, `schema-form`, `rule-tests` |
| **Branch** | `p6-neo4j-graph` |
| **Spec** | `IMPLEMENTATION.md` §5 (model, creation, RUD table, sync), `neo4j-graph/references/cypher.md` |

## Goal
Neo4j holds a live projection of users, skills, projects and collaboration, plus graph-only endorsements and skill relations. Every Read, Update and Delete feature in §5.4 works from the Next.js UI, including vector semantic search.

## Tasks

### Graph backend (`api/app/graph/`)
- [ ] `embed.py`: load `all-MiniLM-L6-v2` once at startup; `embed_project(row)` and `embed_user(row)` return a 384-float list.
- [ ] `cypher.py`: named query constants for every operation in §5.4 and the sync.
- [ ] `sync.py`: fill in the stubs from P1–P4: `upsert_user`, `upsert_user_skills`, `upsert_project` (with embedding), `upsert_membership` (+ `COLLABORATED_WITH` from **Q11**), `deactivate_membership`, `delete_user`. All are idempotent `MERGE`; failures are logged and never raised.
- [ ] `scripts/sync_graph.py --full`: Skills → Users → Projects → HAS_SKILL/REQUIRES/MEMBER_OF/OWNS → COLLABORATED_WITH → embeddings. Print the counts.
- [ ] Seed graph-only data: a `graph/seed_graph.cypher` with about 15 `RELATED_TO` edges (e.g., Docker–Kubernetes, React–Next.js) and about 10 endorsements between seeded collaborators.

### Graph API (`plop router graph`)
- [ ] **Read:**
  - `GET /graph/users/{id}/network?depth=`, `/recommended-collaborators`, `/similar`.
  - `GET /graph/path?from=&to=`.
  - `GET /graph/skills/{id}/related`.
  - `GET /graph/projects/{id}/gap-candidates` (MySQL `SkillGap` + Neo4j related skills + endorsements).
  - `GET /graph/projects/{id}/similar`.
  - `GET /graph/search/projects?q=` (vector).
- [ ] **Update:**
  - `PUT /graph/endorsements` (only if the users collaborated, else 409 `NOT_COLLABORATORS`).
  - `PUT /graph/skills/{a}/related/{b}` (admin).
  - `POST /graph/projects/{id}/reembed` (owner; also called automatically after a project PATCH).
- [ ] **Delete:** `DELETE /graph/endorsements/{to}/{skill_id}`, `DELETE /graph/skills/{a}/related/{b}` (admin).
- [ ] `GET /graph/users/{id}/endorsements` (received, grouped by skill, with average weight).

### Web
- [ ] `components/graph/NetworkGraph.tsx`: `react-force-graph-2d` via `dynamic(..., { ssr: false })`; nodes coloured by "me / collaborator / 2nd degree"; click a node to open the profile.
- [ ] `/graph/network`: the network graph plus a "Recommended collaborators" side list.
- [ ] `/graph/search`: a search box → vector results with similarity scores.
- [ ] `/users/[id]`: profile, endorsements list, an Endorse `Dialog` (skill + 1–5 weight + note) shown only to collaborators, a remove option on your own endorsements, and a "How you're connected" path.
- [ ] `/projects/[id]`: a "Similar projects" card (vector).
- [ ] `/projects/[id]/manage/candidates`: a "Graph suggestions" section (gap-candidates).
- [ ] `/admin/skills`: a related-skills editor (add or update the weight, delete).

### Demo file
- [ ] Fill `graph/003_demo_queries.cypher` with the recommendation, shortest path, related skills, vector search, endorse, update and delete queries, ready to paste into the Neo4j Browser.

### Tests (`test_graph.py`)
- [ ] `sync_graph --full` twice gives identical node and relationship counts.
- [ ] Endorse → weight update → delete, checking the edge count at each step; endorsing a non-collaborator → 409.
- [ ] A member on the related-skill PUT/DELETE → 403.
- [ ] Searching for "machine learning image classifier" returns the seeded ML project first.
- [ ] Accepting an application (P3 flow) creates `MEMBER_OF` and `COLLABORATED_WITH` edges; removing the member sets `MEMBER_OF.active = false`.
- [ ] Neo4j down during an accept → the MySQL accept still commits (sync failure only logged), and the full sync repairs the graph.

## Done when
Every row of the §5.4 table is reachable from the UI and covered by a test, and the vector search works. The gate passes.

## Demo
Neo4j Browser: `MATCH p=(:User {id:2})-[:COLLABORATED_WITH*1..2]-() RETURN p`, then run vector search in the app, then endorse, change the weight and delete it while showing the edge in the Browser.
