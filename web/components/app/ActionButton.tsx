"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { messageFor } from "@/lib/errors";

interface ActionButtonProps {
  label: string;
  method: "POST" | "DELETE" | "PUT";
  path: string;                 // API path, sent through /api/proxy
  body?: unknown;
  success: string;
  confirm?: string;
  variant?: "default" | "outline" | "destructive" | "ghost" | "secondary";
}

/** One-click API action (reject, withdraw, remove...) followed by a refresh. */
export function ActionButton({ label, method, path, body, success, confirm, variant = "outline" }: ActionButtonProps) {
  const router = useRouter();
  const [pending, start] = useTransition();

  const run = () => {
    if (confirm && !window.confirm(confirm)) return;
    start(async () => {
      const res = await fetch(`/api/proxy${path}`, {
        method,
        headers: { "content-type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      if (res.ok) toast.success(success);
      else toast.error(messageFor(await res.json().catch(() => null)));
      router.refresh();
    });
  };

  return <Button size="sm" variant={variant} disabled={pending} onClick={run}>{pending ? "…" : label}</Button>;
}
