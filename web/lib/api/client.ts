// Browser-side typed client. Calls go through /api/proxy, which attaches the
// httpOnly session cookie as a Bearer token, so the JWT never reaches JS.
import createClient from "openapi-fetch";
import type { paths } from "./schema";

export const api = createClient<paths>({ baseUrl: "/api/proxy" });
