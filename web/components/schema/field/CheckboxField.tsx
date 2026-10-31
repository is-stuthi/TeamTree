"use client";

import { Checkbox } from "@/components/ui/checkbox";
import type { FieldProps } from "../types";

export function CheckboxField({ id, value, onChange, onBlur, invalid }: FieldProps) {
  return (
    <Checkbox
      id={id}
      checked={Boolean(value)}
      onCheckedChange={(checked) => { onChange(Boolean(checked)); onBlur(); }}
      aria-invalid={invalid}
    />
  );
}
