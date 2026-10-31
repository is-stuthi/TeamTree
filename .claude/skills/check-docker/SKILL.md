---
name: check-docker
description: Diagnose TeamTREE's Docker Compose setup, including containers not starting, MySQL or Neo4j unhealthy or refusing connections, wrong env vars, and port clashes. Use when the API can't reach a database or `docker compose up` fails.
---

# check-docker

Run these in order and stop at the first failure:

```bash
docker version --format '{{.Server.Version}}'          # daemon running? (start Docker Desktop on Windows)
docker compose config -q && echo compose-ok             # compose file valid?
docker compose ps                                       # db / graph / api state and health
docker compose logs --tail 50 db graph
docker compose exec db mysqladmin ping -uroot -p"$MYSQL_ROOT_PASSWORD"
docker compose exec graph cypher-shell -u neo4j -p "$NEO4J_PASSWORD" 'RETURN 1'
```

Ports: MySQL 3306, Neo4j 7474 (browser) and 7687 (bolt), API 8000, Next.js 3000.
To find what holds a port on Windows: `netstat -ano | findstr :3306`. Stop that service, or remap the port in compose and `.env`.

Env vars that must agree (`.env`, compose, `api/.env`, `web/.env.local`):
- `MYSQL_ROOT_PASSWORD`, `TT_APP_PASSWORD`, `TT_REPORT_PASSWORD`
- `DATABASE_URL=mysql://tt_app:<pw>@<host>:3306/teamtree`
- `NEO4J_URI=bolt://<host>:7687`, `NEO4J_PASSWORD`
- `JWT_SECRET` (the same value in API and web)
- `NEXT_PUBLIC_API_URL`

Use host `db`/`graph` inside compose and `localhost` from the host machine.

Common fixes:
- Stale volume after a schema change: `docker compose down -v`, then `db-migrate` + `neo4j-graph` full sync.
- `Access denied for user 'tt_app'`: `007_rbac.sql` wasn't applied or the password differs. Re-run `db-migrate`.
- Neo4j `Unauthorized` on first boot: `NEO4J_AUTH` is only read when the volume is created; wipe the volume.
- Neo4j out of memory while loading the embedding sync: set `NEO4J_server_memory_heap_max__size=1G`.
- Mounted `.sh` line-ending errors: `git config core.autocrlf input`.

If it still fails after these checks, hand the findings to the `architect` agent.
