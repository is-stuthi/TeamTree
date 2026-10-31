// Pure routing policy used by middleware.ts (unit-tested in route-guard.test.ts).
// UX layer only: FastAPI (require_admin) and MySQL grants are the real enforcement.
import type { Session } from "./session";

const PROTECTED = [
  /^\/dashboard(\/|$)/,
  /^\/admin(\/|$)/,
  /^\/graph(\/|$)/,
  /^\/analytics(\/|$)/,
  /^\/projects\/[^/]+\/manage(\/|$)/,
];
const ADMIN_ONLY = /^\/admin(\/|$)/;
const GUEST_ONLY = /^\/(login|register)\/?$/;

/** Returns the path to redirect to, or null to let the request through. */
export function guard(pathname: string, session: Session | null): string | null {
  if (session && GUEST_ONLY.test(pathname)) return "/dashboard";
  if (!PROTECTED.some((re) => re.test(pathname))) return null;
  if (!session) return `/login?next=${encodeURIComponent(pathname)}`;
  if (ADMIN_ONLY.test(pathname) && session.role !== "admin") return "/dashboard";
  return null;
}

/** Only allow same-site relative redirects after login. */
export function safeNext(next: string | undefined, fallback = "/dashboard"): string {
  return next && next.startsWith("/") && !next.startsWith("//") ? next : fallback;
}
