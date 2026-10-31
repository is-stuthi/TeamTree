import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { getSession } from "@/lib/auth";
import { UserMenu } from "./UserMenu";

export async function SiteHeader() {
  const session = await getSession();
  return (
    <header className="border-b">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <Link href="/" className="font-semibold tracking-tight">TeamTREE</Link>
        <nav className="flex items-center gap-4 text-sm text-muted-foreground">
          <Link href="/projects" className="hover:text-foreground">Projects</Link>
          {session && <Link href="/dashboard" className="hover:text-foreground">Dashboard</Link>}
          {session?.role === "admin" && <Link href="/admin/skills" className="hover:text-foreground">Admin</Link>}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          {session ? (
            <UserMenu name={session.name} role={session.role} />
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
