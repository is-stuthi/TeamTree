# plop templates

| Generator | Files | Notes |
|---|---|---|
| `router` | `api/app/routers/{{snake name}}.py`, `api/app/models/{{snake name}}.py`; appends `include_router` in `api/app/main.py` | Router imports `call_proc`, `fetch_all` from `app.db` and `current_user` from `app.auth`. Includes one example GET. |
| `component` | `web/src/components/app/{{pascal name}}.tsx`, `{{pascal name}}.test.tsx` | Typed props interface, shadcn imports only from `@/components/ui/*`. |
| `page` | `web/src/pages/{{pascal name}}.tsx`; appends a route in `web/src/routes.tsx` | Page = layout + `SchemaForm`/`SchemaDashboard`/app components. No direct fetch calls; use react-query hooks with `api` from `@/api/client`. |

When you add a template, keep its output under 60 lines so it leaves room to grow before reaching the 150-line limit.
