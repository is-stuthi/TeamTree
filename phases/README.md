# TeamTREE — Build phases

Each phase file is self-contained. Load **only the current phase** plus the `IMPLEMENTATION.md` sections it cites.
Work on a branch per phase (`p<N>-<slug>`) and merge through a PR reviewed by a teammate.

| Phase | File | Rubric rows | Depends on | Lead agent |
|---|---|---|---|---|
| P0 ✅ | [P0-foundation.md](P0-foundation.md): Docker, MySQL v2, RBAC, Neo4j, skeletons | 3, 4, 8, 12 | — | architect → builder |
| P1 ✅ | [P1-auth-users.md](P1-auth-users.md): auth, roles, profiles, skills, SchemaForm | 10, 11, 12 | P0 | builder |
| P2 ✅ | [P2-projects.md](P2-projects.md): projects, requirements, discovery | 6, 7 | P1 | builder |
| P3 ✅ | [P3-applications.md](P3-applications.md): apply / withdraw / decide transaction | 6, 8 | P2 | builder (architect review) |
| P4 | [P4-teams-tasks.md](P4-teams-tasks.md): membership, tasks, task tree, transfer | 7, 8 | P3 | builder |
| P5 | [P5-matching.md](P5-matching.md): candidate scoring, skill gap | 7 | P4 | builder |
| P6 | [P6-neo4j-graph.md](P6-neo4j-graph.md): sync, embeddings, graph R/U/D, vector search | 4, 9 | P1 (better after P4) | builder (architect review) |
| P7 | [P7-analytics.md](P7-analytics.md): analytics API + SchemaDashboard | 7, 10 | P5, P6 | builder / sql-scout |
| P8 | [P8-hardening.md](P8-hardening.md): full tests, CI, review, polish | all | P7 | builder |
| P9 | [P9-docs-rubric.md](P9-docs-rubric.md): ER, schema doc, justification, README, viva | 1, 2, 5, 13, 14 | P8 | sql-scout → builder |

```
P0 → P1 → P2 → P3 → P4 → P5 ─┐
            └──────→ P6 ───────┴→ P7 → P8 → P9
```
P6 can start once P1 is merged, in parallel with P2–P5, so a second team member can own it.

## Every phase ends with the same gate
1. `rule-tests` skill: the phase's tests and all earlier tests are green.
2. `cd web && npm run lint && npx tsc --noEmit` passes (150-LOC rule included).
3. `gen-types` skill: `git diff --exit-code web/lib/api/` is clean.
4. `code-review` on the phase diff; apply the fixes.
5. `rubric-check` skill on the phase's rubric rows.
6. Append any new SQL to `db/queries/catalogue.sql` / `dml_demo.sql` (labelled `Qn`/`Dn`) and any demo Cypher to `graph/003_demo_queries.cypher`.
7. PR merged, tag `v0.<N>`.
