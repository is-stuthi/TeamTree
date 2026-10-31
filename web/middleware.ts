import { NextResponse, type NextRequest } from "next/server";
import { guard } from "@/lib/route-guard";
import { SESSION_COOKIE, verifySession } from "@/lib/session";

export async function middleware(req: NextRequest) {
  const token = req.cookies.get(SESSION_COOKIE)?.value;
  const session = await verifySession(token);
  const target = guard(req.nextUrl.pathname, session);
  if (!target) return NextResponse.next();

  const res = NextResponse.redirect(new URL(target, req.url));
  if (token && !session) res.cookies.delete(SESSION_COOKIE);   // expired or tampered
  return res;
}

export const config = {
  matcher: [
    "/dashboard/:path*", "/admin/:path*", "/graph/:path*", "/analytics/:path*",
    "/projects/:id/manage/:path*", "/login", "/register",
  ],
};
