"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { messageFor } from "@/lib/errors";

export interface InlineOption {
  value: string;
  label: string;
}

interface InlineSelectProps {
  value: string;
  options: InlineOption[];
  method: "PATCH" | "POST";
  path: string;                                   // API path via /api/proxy
  field: string;                                  // request body key: { [field]: value }
  kind?: "text" | "id";                           // "id": numeric, and "none" sends null
  label: string;                                  // accessible name
  success: string;                                // toast; "{label}" = chosen option's label
}

// Props must stay serialisable: this client component is rendered from Server Components,
// which cannot pass functions across the boundary.
function toValue(v: string, kind: InlineSelectProps["kind"]) {
  if (kind !== "id") return v;
  return v === "none" ? null : Number(v);
}

/** A select that saves immediately (task status, assignee...) and refreshes. */
export function InlineSelect({ value, options, method, path, field, kind = "text", label, success }: InlineSelectProps) {
  const router = useRouter();
  const [pending, start] = useTransition();

  const save = (next: string | null) => {
    if (next == null || next === value) return;
    start(async () => {
      const res = await fetch(`/api/proxy${path}`, {
        method,
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ [field]: toValue(next, kind) }),
      });
      if (res.ok) toast.success(success.replace("{label}", options.find((o) => o.value === next)?.label ?? next));
      else toast.error(messageFor(await res.json().catch(() => null)));
      router.refresh();
    });
  };

  return (
    <Select items={options} value={value} disabled={pending} onValueChange={save}>
      <SelectTrigger size="sm" className="w-full min-w-32" aria-label={label}><SelectValue /></SelectTrigger>
      <SelectContent>{options.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}</SelectContent>
    </Select>
  );
}
