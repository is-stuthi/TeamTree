// JWT session helpers that run anywhere (middleware/edge, route handlers, RSC).
// The token is issued by FastAPI (/auth/login) and stored in an httpOnly cookie.
import { jwtVerify } from "jose";

export const SESSION_COOKIE = "tt_session";
export const SESSION_MAX_AGE = 60 * 60 * 12;

export type AppRole = "admin" | "member";

export interface Session {
  userId: number;
  role: AppRole;
  name: string;
}

const secret = () => new TextEncoder().encode(process.env.JWT_SECRET ?? "");

export async function verifySession(token: string | undefined): Promise<Session | null> {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify(token, secret(), { algorithms: ["HS256"] });
    const role = payload.role === "admin" ? "admin" : "member";
    return { userId: Number(payload.sub), role, name: String(payload.name ?? "") };
  } catch {
    return null;
  }
}
