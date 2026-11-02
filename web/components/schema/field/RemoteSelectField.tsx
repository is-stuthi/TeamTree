"use client";

import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import type { FieldProps } from "../types";
import { SelectField, type Option } from "./SelectField";

/** Select whose options come from a GET endpoint (hint.source), e.g. the skill catalogue. */
export function RemoteSelectField(props: FieldProps) {
  const { label_key = "name", value_key = "id" } = props.hint;
  const source = props.hint.source?.replace(/\{(\w+)\}/g, (_, k: string) => String(props.params?.[k] ?? ""));
  const { data, isLoading } = useQuery({
    queryKey: ["options", source],
    enabled: Boolean(source),
    queryFn: async (): Promise<Option[]> => {
      const res = await fetch(`/api/proxy${source}`);
      const rows: Record<string, unknown>[] = res.ok ? await res.json() : [];
      return rows.map((r) => ({ value: String(r[value_key!]), label: String(r[label_key!]) }));
    },
  });
  if (isLoading) return <Skeleton className="h-8 w-full" />;
  return <SelectField {...props} options={data ?? []} />;
}
