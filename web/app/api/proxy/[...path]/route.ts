// Same-origin proxy for client components: /api/proxy/<path> -> FastAPI /<path>,
// with the session cookie forwarded as a Bearer token.
import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE } from "@/lib/session";

type Ctx = { params: Promise<{ path: string[] }> };

async function forward(req: NextRequest, { params }: Ctx) {
  const { path } = await params;
  const token = req.cookies.get(SESSION_COOKIE)?.value;
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (token) headers.authorization = `Bearer ${token}`;

  const hasBody = !["GET", "HEAD"].includes(req.method);
  const upstream = await fetch(`${process.env.API_URL}/${path.join("/")}${req.nextUrl.search}`, {
    method: req.method,
    headers,
    body: hasBody ? await req.text() : undefined,
  });
  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
  });
}

export { forward as GET, forward as POST, forward as PUT, forward as PATCH, forward as DELETE };
