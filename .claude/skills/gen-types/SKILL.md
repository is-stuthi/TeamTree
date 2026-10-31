---
name: gen-types
description: Regenerate TeamTREE's TypeScript definitions (web/lib/api/schema.d.ts from FastAPI OpenAPI, ui-schemas.d.ts from the UI JSON specs). Use after changing any Pydantic model, endpoint, or api/app/ui_schemas module, or when the Next.js app reports type errors against the API.
---

# gen-types

The generated `.d.ts` files are the **only** place Claude should read the API contract from.

## Run
```bash
cd api && uv run python scripts/dump_openapi.py      # writes api/openapi.json and api/ui_schemas_out/*.json
cd ../web && npm run gen                              # openapi-typescript + json2ts → lib/api/*.d.ts
git diff --stat lib/api/                              # review what changed
npx tsc --noEmit                                      # surface breakages in pages and components
```

## Rules
- Never hand-edit `lib/api/schema.d.ts` or `lib/api/ui-schemas.d.ts`.
- If `tsc` breaks after regeneration, fix the callers. Don't loosen types with `any`.
- In CI or before committing: `npm run gen && git diff --exit-code lib/api/` must pass.
