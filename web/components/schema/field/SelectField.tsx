"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { FieldProps } from "../types";

export interface Option {
  value: string;
  label: string;
}

/** Enum select. Also used by RemoteSelectField with options fetched from the API. */
export function SelectField({ id, prop, hint, value, onChange, onBlur, invalid, options }: FieldProps & { options?: Option[] }) {
  const items = options ?? (prop.enum ?? []).map((v) => ({ value: v, label: v }));
  const current = value === "" || value == null ? null : String(value);
  return (
    <Select
      items={items}
      value={current}
      onValueChange={(v) => onChange(v ?? "")}
      onOpenChange={(open) => !open && onBlur()}
    >
      <SelectTrigger id={id} className="w-full" aria-invalid={invalid}>
        <SelectValue placeholder={hint.placeholder ?? "Select…"} />
      </SelectTrigger>
      <SelectContent>
        {items.map((o) => (
          <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
