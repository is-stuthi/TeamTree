// Server-only session access (Server Components, route handlers).
import { cookies } from "next/headers";
import { SESSION_COOKIE, verifySession, type Session } from "./session";

export async function getToken(): Promise<string | undefined> {
  return (await cookies()).get(SESSION_COOKIE)?.value;
}

export async function getSession(): Promise<Session | null> {
  return verifySession(await getToken());
}
