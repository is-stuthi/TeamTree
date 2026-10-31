# plop templates

| Generator | Files | Notes |
|---|---|---|
| `router` | `api/app/routers/{{snake name}}.py`, `api/app/models/{{snake name}}.py`, `api/app/queries/{{snake name}}.py`; appends `include_router` in `api/app/main.py` | Router imports `call_proc`, `fetch_all` from `app.db`, `current_user`/`require_role` from `app.auth`. One example GET. |
| `component` | `web/components/app/{{pascal name}}.tsx`, `{{pascal name}}.test.tsx` | Typed props; shadcn imports from `@/components/ui/*`. Server component unless `--client` adds `"use client"`. |
| `page` | `web/app/{{route}}/page.tsx`, `web/app/{{route}}/loading.tsx` | Async Server Component: `const api = await serverApi()`, then render `SchemaForm`/`SchemaDashboard`/app components. Protected routes sit under `(dashboard)`, `admin` or `graph`, which `middleware.ts` guards. |

When you add a template, keep its output under 60 lines so it leaves room to grow before reaching the 150-line limit.
