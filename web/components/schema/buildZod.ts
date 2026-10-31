// JSON Schema (from the Pydantic models) -> zod, so the browser validates with
// exactly the rules the API enforces.
import { z } from "zod";
import type { FormSchema, FormValues, JsonProp } from "./types";

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const emptyToUndefined = (v: unknown) => (v === "" || v === null ? undefined : v);

function base(prop: JsonProp): z.ZodType {
  if (prop.enum) return z.enum(prop.enum as [string, ...string[]], { error: "Choose an option" });
  if (prop.type === "integer" || prop.type === "number") {
    let n = z.coerce.number({ error: "Enter a number" });
    if (prop.type === "integer") n = n.int();
    if (prop.minimum != null) n = n.min(prop.minimum);
    if (prop.maximum != null) n = n.max(prop.maximum);
    return n;
  }
  if (prop.type === "boolean") return z.boolean();
  if (prop.type === "array") return z.array(z.string());
  let s = z.string().trim();
  if (prop.minLength) s = s.min(prop.minLength, `At least ${prop.minLength} characters`);
  if (prop.maxLength) s = s.max(prop.maxLength, `At most ${prop.maxLength} characters`);
  if (prop.format === "email") s = s.regex(EMAIL, "Enter a valid email");
  if (prop.format === "date") s = s.regex(DATE, "Use YYYY-MM-DD");
  return s;
}

export function fieldSchema(prop: JsonProp, required: boolean): z.ZodType {
  const optional = z.preprocess(emptyToUndefined, base(prop).optional());
  return required ? optional.refine((v) => v !== undefined, "Required") : optional;
}

export function buildZod(schema: FormSchema) {
  const required = new Set(schema.required ?? []);
  const shape = Object.fromEntries(
    Object.entries(schema.properties).map(([name, prop]) => [name, fieldSchema(prop, required.has(name))]),
  );
  return z.object(shape);
}

/** Initial form state: API values when editing, otherwise empty controls. */
export function initialValues(schema: FormSchema, values: FormValues = {}): FormValues {
  return Object.fromEntries(
    Object.entries(schema.properties).map(([name, prop]) => {
      const v = values[name] ?? prop.default;
      if (prop.type === "boolean") return [name, Boolean(v)];
      if (prop.type === "array") return [name, Array.isArray(v) ? v : []];
      return [name, v == null ? "" : String(v)];
    }),
  );
}
