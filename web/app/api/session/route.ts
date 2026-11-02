// Login / register / logout. Forwards credentials to FastAPI and keeps the JWT
// in an httpOnly cookie so client JavaScript never sees it.
import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE, SESSION_MAX_AGE } from "@/lib/session";

export async function POST(req: NextRequest) {
  const mode = req.nextUrl.searchParams.get("mode") === "register" ? "register" : "login";
  let upstream: Response;
  try {
    upstream = await fetch(`${process.env.API_URL}/auth/${mode}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: await req.text(),
    });
  } catch {
    return NextResponse.json({ code: "API_UNAVAILABLE", message: "The server is unreachable." }, { status: 502 });
  }
  // Non-JSON upstream errors (proxy pages, crashes) must not crash this handler.
  const data = await upstream.json().catch(() => ({ code: "UPSTREAM_ERROR", message: `Server error (${upstream.status})` }));
  if (!upstream.ok) return NextResponse.json(data, { status: upstream.status });

  const res = NextResponse.json({ user: data.user }, { status: upstream.status });
  res.cookies.set(SESSION_COOKIE, data.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_MAX_AGE,
  });
  return res;
}

export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.cookies.delete(SESSION_COOKIE);
  return res;
}
