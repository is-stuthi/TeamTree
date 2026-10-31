---
name: scaffold
description: Generate TeamTREE boilerplate with plop (FastAPI router, React component, Next.js App Router page) and add shadcn/ui primitives with the shadcn CLI. Also use when a source file approaches the 150-line limit and must be split.
---

# scaffold

## Generators
```bash
cd web && npx plop router <name>        # api/app/routers/<name>.py + models/ + queries/ + registers in main.py
cd web && npx plop component <Name>     # components/app/<Name>.tsx (+ test)
cd web && npx plop page <route/path>    # app/<route/path>/page.tsx (+ loading.tsx)
cd web && npx shadcn@latest add <primitive> [...]
```
Templates live in `web/plop-templates/`. See `references/templates.md` for what each one emits.
After `plop router`, run the `gen-types` skill.

## 150-line rule
ESLint `max-lines` (150, ignoring blank lines and comments) fails the build. Python files follow the same limit by review. When a file nears it:
1. Extract data fetching into a server helper (`lib/…`) or a client hook (`useXxx.ts`).
2. Extract repeated JSX into sibling components in the same folder.
3. If the JSX is a form or a dashboard, replace it with a JSON spec (`schema-form` skill).
4. Backend: move SQL to `app/queries/<router>.py` and Cypher to `app/graph/cypher.py`; keep routers to endpoint wiring.

Exempt: `components/ui/**` (shadcn) and the generated `lib/api/*.d.ts`.

## Route groups and redirects
- `app/(public)`: anyone. `app/(dashboard)`: logged in. `app/admin`: admin. `app/(manage)/projects/[id]/manage`: owner only (its layout checks `viewer.is_owner`).
- A layout that calls `redirect()` must not have a `loading.tsx` in an **ancestor** segment. That boundary starts streaming, which turns the redirect into a client-side meta refresh with HTTP 200. This is why the manage area lives in its own `(manage)` group, away from `(public)/projects/loading.tsx`. A `loading.tsx` in the *same* segment as the layout is fine.
- Base UI shadcn (`base-nova`) has no `asChild`. Style links with `buttonVariants()`, and use `SpecDialog` for forms in dialogs and `ActionButton` for one-click API calls.
