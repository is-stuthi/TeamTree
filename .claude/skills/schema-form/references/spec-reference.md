# Spec reference

## Form field widgets (`ui.fields.<field>.widget`)

| widget | JSON Schema type | shadcn component | extra keys |
|---|---|---|---|
| (default) | string | Input | `placeholder` |
| `textarea` | string | Textarea | `rows` |
| `number` | integer/number | Input type=number | `min`, `max`, `step` |
| (enum) | string + `enum` | Select | `labels` (value → label) |
| `date` | string `format: date` | Popover + Calendar | `minDate: "today"` |
| `checkbox` | boolean | Checkbox | — |
| `tags` | array of string | Input + Badge | `suggestSource` (GET path) |
| `skill-level` | array of `{s_id, level}` | Select + Select rows | `source: "/skills"` |
| `password` | string | Input type=password | — |

Common keys: `label`, `help`, `hidden`, `colSpan`.

## Form example: `application_create`
```json
{
  "name": "application_create",
  "title": "Apply to project",
  "submit": { "method": "POST", "path": "/projects/{p_id}/applications" },
  "schema": { "type": "object", "required": ["msg"],
    "properties": { "msg": { "type": "string", "minLength": 20, "maxLength": 2000, "title": "Why you?" } } },
  "ui": { "order": ["msg"], "fields": { "msg": { "widget": "textarea", "rows": 6 } } }
}
```
Path params such as `{p_id}` are filled from the `params` prop of `<SchemaForm>`.

## Dashboard widgets

| type | required keys | optional |
|---|---|---|
| `stat` | `title`, `source`, `path` | `format: number\|percent\|days` |
| `bar` | `title`, `source`, `x`, `series[]` | `stacked`, `span` |
| `pie` | `title`, `source`, `path` (object of label → count) | `span` |
| `table` | `title`, `source`, `columns[]` | `pageSize`, `span` |
| `progress` | `title`, `source`, `value`, `max` | `span` |
| `line` | `title`, `source`, `x`, `y` | `span` (e.g., Q9 applications per day) |
| `graph` | `title`, `source` (returns `{nodes, edges}`) | `height`, `span` (Neo4j network, client-only) |

`source` may contain `{id}`; it is filled from the dashboard's `params` prop. `path` is dot-notation into the response.
