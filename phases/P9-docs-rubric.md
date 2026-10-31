# P9 — Documentation, rubric pack & viva prep

| | |
|---|---|
| **Rubric** | 1 ER (2), 2 relational schema (3), 5 tech justification (1), 13 docs + Git (2), 14 originality/contribution/viva (4) |
| **Depends on** | P8 (doc drafts can start earlier) |
| **Agents** | `sql-scout` drafts tables and lists · `builder` reviews and finalises |
| **Skills** | `rubric-check`, `run` (screenshots) |
| **Branch** | `p9-docs` |
| **Spec** | `IMPLEMENTATION.md` §0 (rubric map), §11 (doc contents) |

## Goal
Every rubric row has polished, findable evidence. Every team member can demo and explain their slice.

## Tasks

### Rubric 1: ER diagram
- [ ] `docs/er.mmd`: a Mermaid ER of the final schema (source of truth, diff-able).
- [ ] Redraw `docs/ER Diagram.png` in Chen notation with:
  - Entities: USER, SKILL, PROJECT, APPLICATION, TEAM, TASK.
  - Relationships: HAS (u_s_level), CREATES/OWNS, REQUIRES (level, role, count), SUBMITS, RECEIVES, REVIEWS (decision_date), HAS team, JOINS (role, join_date, leave_date), CONTAINS, ASSIGNED_TO, SUBTASK_OF (recursive), TRANSFERS (Ownership_Transfer).
  - Attribute notation: derived `age`, multivalued `domain`, composite `name`; the new attributes `role`, `max_team_size`, `Withdrawn` status.
  - Cardinality and participation on every relationship.

### Rubric 2: relational schema
- [ ] `docs/RELATIONAL_SCHEMA.md`:
  - Per table: attributes + types, PK, FKs with the ON DELETE choice and why, UNIQUE, CHECK, generated columns.
  - An ER → relation mapping table (which rule mapped each relationship).
  - Functional dependencies per table and a 3NF/BCNF argument.
  - The generated-flag "one active row" technique explained.

### Rubric 5: technology justification
- [ ] `docs/TECH_JUSTIFICATION.md` (1–2 pages):
  - MySQL: ACID, CHECK/FK, procedures, roles.
  - Neo4j: multi-hop traversal and a native vector index; compared against MongoDB and pgvector.
  - FastAPI: OpenAPI → TS types, raw SQL kept visible.
  - Next.js + shadcn: App Router, middleware auth, rubric fit.
  - Docker.
  - A short "alternatives considered" table.

### Rubric 13: docs & Git
- [ ] `README.md`: one-paragraph pitch, architecture diagram (MySQL ↔ FastAPI ↔ Neo4j, Next.js), setup steps, demo accounts, a feature list with screenshots (`docs/screenshots/`), the rubric map table linking to evidence, and how to run the tests.
- [ ] Confirm that every phase has a merged PR and a tag `v0.0`…`v0.9`; tag `v1.0`.
- [ ] Keep `IMPLEMENTATION.md` and `phases/*` in the repo as the design trail.

### Rubric 14: originality, contribution, viva
- [ ] `docs/CONTRIBUTIONS.md`: member → owned phases and files, with links to their PRs and commit counts (`git shortlog -sn`). Replace the placeholder split with the real one.
- [ ] `docs/VIVA_NOTES.md`:
  - 2–3 likely questions per member's slice, with crisp answers. Include: why a derived reviewer, the generated-flag uniqueness, DEFINER procedures + RBAC, `FOR UPDATE` lock order, normal forms, why a graph DB, how the vector index works (cosine, 384 dimensions), sync consistency, matching weights.
  - A "modification drill" list: small live changes examiners often ask for (add a column + CHECK, add a trigger, add a Cypher query, add a form field via JSON). Each should be rehearsed once.
- [ ] Practise the `rubric-check` demo script (5 minutes, in rubric order) with each member presenting their own part.

## Done when
`rubric-check` reports ✅ on all 14 rows, README setup is verified on a teammate's machine, and every member has rehearsed their viva section and one modification drill.
