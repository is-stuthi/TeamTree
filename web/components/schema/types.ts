import type { components } from "@/lib/api/schema";

export type UiSpec = components["schemas"]["UiSpec"];
export type FieldHint = Partial<components["schemas"]["FieldHint"]>;
export type Widget = NonNullable<components["schemas"]["FieldHint"]["widget"]>;
export type FormValues = Record<string, unknown>;

/** The simplified JSON Schema emitted by api/app/ui_schemas/base.py. */
export interface JsonProp {
  type?: string;
  enum?: string[];
  format?: string;
  title?: string;
  minLength?: number;
  maxLength?: number;
  minimum?: number;
  maximum?: number;
  default?: unknown;
  items?: JsonProp;
}

export interface FormSchema {
  properties: Record<string, JsonProp>;
  required?: string[];
}

export interface FieldProps {
  id: string;
  name: string;
  prop: JsonProp;
  hint: FieldHint;
  value: unknown;
  onChange: (value: unknown) => void;
  onBlur: () => void;
  invalid: boolean;
  params?: Record<string, string | number>;   // fills {placeholders} in remote-select sources
}

export const formSchema = (spec: UiSpec) => spec.schema as unknown as FormSchema;

export function widgetFor(prop: JsonProp, hint: FieldHint): Widget {
  if (hint.widget) return hint.widget;
  if (prop.enum) return "select";
  if (prop.type === "boolean") return "checkbox";
  if (prop.type === "array") return "tags";
  if (prop.type === "integer" || prop.type === "number") return "number";
  if (prop.format === "password" || prop.format === "email" || prop.format === "date") return prop.format;
  return "text";
}
