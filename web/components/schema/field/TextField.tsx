import { Input } from "@/components/ui/input";
import type { FieldProps, Widget } from "../types";

const INPUT_TYPE: Partial<Record<Widget, string>> = {
  password: "password", email: "email", date: "date", number: "number",
};

export function TextField({ id, name, prop, hint, value, onChange, onBlur, invalid, widget }: FieldProps & { widget: Widget }) {
  return (
    <Input
      id={id}
      name={name}
      type={INPUT_TYPE[widget] ?? "text"}
      value={String(value ?? "")}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      placeholder={hint.placeholder ?? undefined}
      maxLength={prop.maxLength}
      autoComplete={widget === "password" ? "current-password" : widget === "email" ? "email" : undefined}
      aria-invalid={invalid}
      aria-describedby={invalid ? `${id}-error` : undefined}
    />
  );
}
