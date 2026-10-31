"use client";

import { Controller, type Control } from "react-hook-form";
import { CheckboxField } from "./field/CheckboxField";
import { RemoteSelectField } from "./field/RemoteSelectField";
import { SelectField } from "./field/SelectField";
import { TagsField } from "./field/TagsField";
import { TextareaField } from "./field/TextareaField";
import { TextField } from "./field/TextField";
import { FieldShell } from "./FieldShell";
import { widgetFor, type FieldHint, type FieldProps, type FormValues, type JsonProp } from "./types";

interface FieldRendererProps {
  formId: string;
  name: string;
  prop: JsonProp;
  hint: FieldHint;
  required: boolean;
  control: Control<FormValues>;
}

function Widget(props: FieldProps) {
  const widget = widgetFor(props.prop, props.hint);
  switch (widget) {
    case "textarea": return <TextareaField {...props} />;
    case "select": return <SelectField {...props} />;
    case "remote-select": return <RemoteSelectField {...props} />;
    case "checkbox": return <CheckboxField {...props} />;
    case "tags": return <TagsField {...props} />;
    default: return <TextField {...props} widget={widget} />;
  }
}

export function FieldRenderer({ formId, name, prop, hint, required, control }: FieldRendererProps) {
  const id = `${formId}-${name}`;
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <FieldShell id={id} label={hint.label ?? prop.title ?? name} required={required}
                    help={hint.help} error={fieldState.error?.message}>
          <Widget id={id} name={name} prop={prop} hint={hint} value={field.value}
                  onChange={field.onChange} onBlur={field.onBlur} invalid={Boolean(fieldState.error)} />
        </FieldShell>
      )}
    />
  );
}
