"use client";

import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";
import { messageFor } from "@/lib/errors";
import { buildQuery, buildRequest, type RequestOptions } from "./request";
import type { FormValues, UiSpec } from "./types";

export interface SubmitOptions extends RequestOptions {
  redirectTo?: string;
  onDone?: () => void;
}

export function useSubmitSpec(spec: UiSpec, opts: SubmitOptions) {
  const router = useRouter();
  const pathname = usePathname();

  return async (values: FormValues) => {
    if (spec.submit.method === "GET") {           // search form: navigate, don't call the API
      const qs = buildQuery(values);
      router.push(qs ? `${pathname}?${qs}` : pathname);
      return;
    }
    const { url, method, body } = buildRequest(spec, values, opts);
    const res = await fetch(url, {
      method,
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      toast.error(messageFor(data));
      return;
    }
    if (spec.success_message) toast.success(spec.success_message);
    opts.onDone?.();
    if (opts.redirectTo) router.push(opts.redirectTo);
    router.refresh();
  };
}
