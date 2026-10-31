import { Textarea } from "@/components/ui/textarea";
import type { FieldProps } from "../types";

export function TextareaField({ id, name, prop, hint, value, onChange, onBlur, invalid }: FieldProps) {
  return (
    <Textarea
      id={id}
      name={name}
      rows={hint.rows ?? 4}
      value={String(value ?? "")}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      placeholder={hint.placeholder ?? undefined}
      maxLength={prop.maxLength}
      aria-invalid={invalid}
      aria-describedby={invalid ? `${id}-error` : undefined}
    />
  );
}
