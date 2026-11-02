// Server-side typed client for Server Components: talks to FastAPI directly.
import { cache } from "react";
import createClient from "openapi-fetch";
import { getToken } from "@/lib/auth";
import type { components, paths } from "./schema";

export type UiSpec = components["schemas"]["UiSpec"];
export type Me = components["schemas"]["UserMe"];

export async function serverApi() {
  const token = await getToken();
  return createClient<paths>({
    baseUrl: process.env.API_URL,
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

export async function getSpec(name: string): Promise<UiSpec> {
  const api = await serverApi();
  const { data, error } = await api.GET("/ui-schemas/{name}", { params: { path: { name } } });
  if (!data) throw new Error(`UI spec "${name}" unavailable: ${JSON.stringify(error)}`);
  return data;
}

/** The *current* user as the API sees it (role and active status re-read on every
 *  request), deduplicated per render. null = not logged in, expired or deactivated.
 *  Use this, not the JWT claims, for anything that depends on role. */
export const getMe = cache(async (): Promise<Me | null> => {
  if (!(await getToken())) return null;
  const { data } = await (await serverApi()).GET("/auth/me");
  return data ?? null;
});

/** Untyped GET for spec-driven widgets whose source path comes from JSON. Returns
 *  null on any error so one failing widget can't break a whole dashboard. */
export const fetchSource = cache(async (path: string): Promise<unknown> => {
  const token = await getToken();
  try {
    const res = await fetch(`${process.env.API_URL}${path}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      cache: "no-store",
    });
    return res.ok ? await res.json() : null;
  } catch {
    return null;
  }
});

/** Project detail, deduplicated per render (layout + page share one request). */
export const getProject = cache(async (p_id: number) => {
  const { data } = await (await serverApi()).GET("/projects/{p_id}", { params: { path: { p_id } } });
  return data ?? null;
});
