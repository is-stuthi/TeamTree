---
name: scaffold
description: Generate TeamTREE boilerplate with plop (FastAPI router, React component, page) and add shadcn/ui primitives with the shadcn CLI. Also use when a source file approaches the 150-line limit and must be split.
---

# scaffold

## Generators
```bash
cd web && npx plop router <name>      # api/app/routers/<name>.py + models/<name>.py + registers in main.py
cd web && npx plop component <Name>   # src/components/app/<Name>.tsx (+ <Name>.test.tsx)
cd web && npx plop page <Name>        # src/pages/<Name>.tsx + route entry
cd web && npx shadcn@latest add <primitive> [...]
```
Templates live in `web/plop-templates/`. See `references/templates.md` for what each one emits.
After `plop router`, run the `gen-types` skill.

## 150-line rule
The ESLint `max-lines` rule (150, ignoring blank lines and comments) fails the build. When a file nears the limit:
1. Extract data fetching into a `useXxx.ts` hook.
2. Extract repeated JSX blocks into sibling components in the same folder.
3. If the JSX is a form or a dashboard, replace it with a JSON spec (`schema-form` skill).
4. Backend: move SQL into `app/queries/<router>.py` and keep the router to endpoint wiring.

Exempt: `src/components/ui/**` (shadcn) and the generated `src/api/*.d.ts`.
