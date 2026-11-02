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
  toBody: (value: string) => unknown;
  label: string;                                  // accessible name
  success: (label: string) => string;
}

/** A select that saves immediately (task status, assignee...) and refreshes. */
export function InlineSelect({ value, options, method, path, toBody, label, success }: InlineSelectProps) {
  const router = useRouter();
  const [pending, start] = useTransition();

  const save = (next: string | null) => {
    if (next == null || next === value) return;
    start(async () => {
      const res = await fetch(`/api/proxy${path}`, {
        method,
        headers: { "content-type": "application/json" },
        body: JSON.stringify(toBody(next)),
      });
      if (res.ok) toast.success(success(options.find((o) => o.value === next)?.label ?? next));
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
