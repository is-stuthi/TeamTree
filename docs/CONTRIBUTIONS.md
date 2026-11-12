# Contributions

> **To the team:** replace the placeholders below with your names and the work each of you actually
> did, and link your own PRs and commits. Evaluators check this against the Git history
> (`git shortlog -sn`), so be accurate. A suggested split by vertical slice is pre-filled; edit it freely.

| Member | Slice owned | Main files | Rubric rows |
|---|---|---|---|
| _Name 1_ | Database design & SQL: schema v2, functions, triggers, procedures, views, query catalogue | `db/`, `docs/RELATIONAL_SCHEMA.md` | 1, 2, 3, 6, 7, 8 |
| _Name 2_ | Neo4j: graph model, sync, vector search, endorsements | `graph/`, `api/app/graph/`, `api/app/routers/graph*.py` | 4, 9 |

## How to verify

```bash
git shortlog -sn --all          # commits per author
git log --author="<name>" --stat
```

Every member should be able to demo and explain their slice and answer the matching questions in
[VIVA_NOTES.md](VIVA_NOTES.md).
