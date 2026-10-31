import type { FormValues, UiSpec } from "./types";

export interface RequestOptions {
  action?: string;                                  // override URL (e.g. /api/session)
  method?: string;
  params?: Record<string, string | number>;         // path params not present in the form
}

/** GET specs are search forms: non-empty values become the page's query string. */
export function buildQuery(values: FormValues): string {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(values)) {
    if (v === undefined || v === null || v === "" || (Array.isArray(v) && v.length === 0)) continue;
    qs.set(k, String(v));
  }
  return qs.toString();
}

/** Fill {placeholders} in spec.submit.path from params/values; path fields leave the body. */
export function buildRequest(spec: UiSpec, values: FormValues, opts: RequestOptions = {}) {
  const used = new Set<string>();
  const path = spec.submit.path.replace(/\{(\w+)\}/g, (_, key: string) => {
    used.add(key);
    return encodeURIComponent(String(opts.params?.[key] ?? values[key] ?? ""));
  });
  const body = Object.fromEntries(
    Object.entries(values).filter(([k, v]) => !used.has(k) && v !== undefined),
  );
  return {
    url: opts.action ?? `/api/proxy${path}`,
    method: opts.method ?? spec.submit.method,
    body,
  };
}
