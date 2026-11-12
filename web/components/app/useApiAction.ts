"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { messageFor } from "@/lib/errors";

export interface ApiAction {
  method: "POST" | "DELETE" | "PUT";
  path: string;                 // API path, sent through /api/proxy
  body?: unknown;
  success: string;
}

/** Call the API through the proxy, toast the outcome, refresh server components. */
export function useApiAction() {
  const router = useRouter();
  const [pending, start] = useTransition();

  const run = ({ method, path, body, success }: ApiAction) =>
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

  return { pending, run };
}
