---
name: check-docker
description: Diagnose TeamTREE's Docker Compose setup, including containers not starting, MySQL unhealthy or refusing connections, wrong env vars, and port clashes. Use when the API can't reach the DB or `docker compose up` fails.
---

# check-docker

Run these in order and stop at the first failure:

```bash
docker version --format '{{.Server.Version}}'          # daemon running?
docker compose config -q && echo compose-ok             # compose file valid?
docker compose ps                                       # db state / health
docker compose logs --tail 50 db                        # init errors, bad SQL, auth plugin
docker compose exec db mysqladmin ping -uroot -p"$MYSQL_ROOT_PASSWORD"
```

Port 3306 already in use (Windows: `netstat -ano | findstr 3306`): stop the local MySQL service, or remap to `"3307:3306"` and update `DATABASE_URL`.

Env vars that must agree (`.env`, `docker-compose.yml`, `api/.env`):
`MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE=teamtree`, `DATABASE_URL=mysql://root:<pw>@localhost:<port>/teamtree` (use host `db` instead of `localhost` when the API runs inside compose).

Common fixes:
- Stale volume after a schema change: `docker compose down -v`, then the `db-migrate` skill.
- `Public Key Retrieval is not allowed` / auth plugin errors: the driver needs `caching_sha2_password` support (aiomysql ≥ 0.2 with `cryptography` installed).
- Line-ending errors in mounted `.sh`: set `git config core.autocrlf input`.

If it still fails after these checks, hand the full findings to the `architect` agent.
