"use client";

// Static renderer for API-provided form specs (schema-driven UI).
// New forms are JSON specs (api/app/ui_schemas/*), not new JSX.
import { useId, useMemo } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { buildZod, initialValues } from "./buildZod";
import { FieldRenderer } from "./FieldRenderer";
import { formSchema, type FormValues, type UiSpec } from "./types";
import { useSubmitSpec, type SubmitOptions } from "./useSubmitSpec";

export interface SchemaFormProps extends Omit<SubmitOptions, "onDone"> {
  spec: UiSpec;
  defaultValues?: FormValues;
  resetOnSuccess?: boolean;
  submitLabel?: string;
  onSuccess?: () => void;       // client wrappers only (e.g. close a dialog)
}

export function SchemaForm({ spec, defaultValues, resetOnSuccess, submitLabel, onSuccess, ...opts }: SchemaFormProps) {
  const formId = useId();
  const schema = formSchema(spec);
  const resolver = useMemo(() => zodResolver(buildZod(schema)), [schema]);
  const form = useForm<FormValues>({ resolver, defaultValues: initialValues(schema, defaultValues) });
  const submit = useSubmitSpec(spec, {
    ...opts,
    onDone: () => {
      if (resetOnSuccess) form.reset(initialValues(schema));
      onSuccess?.();
    },
  });
  const required = new Set(schema.required ?? []);
  const fields = spec.ui.fields ?? {};

  return (
    <form onSubmit={form.handleSubmit(submit)} className="grid gap-4" noValidate aria-label={spec.title}>
      {spec.ui.order.filter((name) => !fields[name]?.hidden && schema.properties[name]).map((name) => (
        <FieldRenderer key={name} formId={formId} name={name} prop={schema.properties[name]}
                       hint={fields[name] ?? {}} required={required.has(name)} control={form.control} />
      ))}
      <Button type="submit" disabled={form.formState.isSubmitting} className="justify-self-start">
        {form.formState.isSubmitting ? "Saving…" : submitLabel ?? spec.submit_label}
      </Button>
    </form>
  );
}
