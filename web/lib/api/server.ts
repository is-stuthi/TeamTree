// Server-side typed client for Server Components: talks to FastAPI directly.
import createClient from "openapi-fetch";
import { getToken } from "@/lib/auth";
import type { components, paths } from "./schema";

export type UiSpec = components["schemas"]["UiSpec"];

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
