---
name: neo4j-graph
description: Work with TeamTREE's Neo4j graph + vector store. Covers applying constraints and vector indexes, running the MySQL → Neo4j sync, regenerating embeddings, and writing Cypher for the read/update/delete graph endpoints. Use for anything under graph/, api/app/graph/, or /graph/* endpoints.
---

# neo4j-graph

MySQL is the system of record. Neo4j holds a **projection** (User, Skill, Project, HAS_SKILL, REQUIRES, MEMBER_OF, OWNS, COLLABORATED_WITH) plus **graph-only data** (ENDORSES, RELATED_TO, `embedding` properties). Model and endpoints: `IMPLEMENTATION.md` §5.

## Create / reset
```bash
docker compose up -d graph
cd api && .venv/Scripts/python scripts/graph_init.py           # constraints + vector indexes (add --reset to wipe)
cd api && .venv/Scripts/python scripts/sync_graph.py --full    # (P6) MERGE all nodes/edges + embeddings
```
Check: `SHOW CONSTRAINTS; SHOW VECTOR INDEXES;` (state must be `ONLINE`), then `MATCH (n) RETURN labels(n)[0], count(*);`.
Full reset (this loses endorsements and RELATED_TO): `MATCH (n) DETACH DELETE n`, then the steps above.

## Writing Cypher
Read `references/cypher.md` before adding a query. Rules in short:
- Always use parameters (`$uid`), never string formatting.
- Sync uses `MERGE` on the id, then `SET`. It never touches ENDORSES or RELATED_TO.
- Put every query in `api/app/graph/cypher.py` as a named constant, and mirror the demo-worthy ones in `graph/003_demo_queries.cypher`.
- Vector queries: `db.index.vector.queryNodes(index, k, $vec)`. Embed with `app/graph/embed.py` (all-MiniLM-L6-v2, 384 dimensions, cosine).

Sync design or consistency changes go to the `architect` agent.
