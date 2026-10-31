---
name: schema-form
description: Add or change a TeamTREE form or dashboard by writing a JSON spec that the static SchemaForm / SchemaDashboard components render with shadcn. Use for any new form, filter panel, analytics dashboard, or field/widget change, instead of writing JSX.
---

# schema-form

Output **JSON only**. The renderers in `web/src/components/schema/` are static and should rarely change.

## Forms
1. Make sure a Pydantic model exists for the payload (backend `api/app/models/`). This gives the validation rules.
2. Add `api/app/ui_schemas/<name>.py` returning `{name, title, submit:{method,path}, schema, ui:{order, fields}}`.
3. Run the `gen-types` skill.
4. Use it in a page: `<SchemaForm name="<name>" onSuccess={…} />`.

Client-only forms (filters) can instead live as `web/src/specs/forms/<name>.json`.

## Dashboards
Write `web/src/specs/dashboards/<name>.json` with `{title, grid:{cols}, widgets:[…]}` and render it with `<SchemaDashboard name="<name>" />`. Data comes from `/analytics/*` or other GET endpoints; widgets never compute metrics themselves (SQL views do).

Field widgets, widget types and full examples: `references/spec-reference.md`.
Chart colours and legends: follow the `dataviz` skill.

Only add a new widget type when no existing type fits. When you do, add a file under `field/` or `widget/` (≤ 150 lines) and a case in the matching `*Renderer.tsx`.
