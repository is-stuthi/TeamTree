import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { getMe } from "@/lib/api/server";
import { UserMenu } from "./UserMenu";

export async function SiteHeader() {
  // Live role from the API, so promotions/demotions show up without re-login.
  const me = await getMe();
  const name = me ? `${me.f_name} ${me.l_name}` : "";
  return (
    <header className="border-b">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <Link href="/" className="font-semibold tracking-tight">TeamTREE</Link>
        <nav className="flex items-center gap-4 text-sm text-muted-foreground">
          <Link href="/projects" className="hover:text-foreground">Projects</Link>
          {me && <Link href="/dashboard" className="hover:text-foreground">Dashboard</Link>}
          {me && <Link href="/graph/network" className="hover:text-foreground">Network</Link>}
          {me && <Link href="/analytics" className="hover:text-foreground">Analytics</Link>}
          {me?.role === "admin" && <Link href="/admin/skills" className="hover:text-foreground">Admin</Link>}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          {me ? (
            <UserMenu name={name} role={me.role} />
          ) : (
            <>
              <Link href="/login" className={buttonVariants({ variant: "ghost", size: "sm" })}>Log in</Link>
              <Link href="/register" className={buttonVariants({ size: "sm" })}>Sign up</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
