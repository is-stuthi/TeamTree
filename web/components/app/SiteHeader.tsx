import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { getMe } from "@/lib/api/server";
import { Logo } from "./Logo";
import { MainNav } from "./MainNav";
import { UserMenu } from "./UserMenu";

export async function SiteHeader() {
  // Live role from the API, so promotions/demotions show up without re-login.
  const me = await getMe();
  const name = me ? `${me.f_name} ${me.l_name}` : "";
  const items = [{ href: "/projects", label: "Projects" }, ...(me ? [{ href: "/dashboard", label: "Dashboard" }] : [])];
  return (
    <header className="bg-background/80 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40 border-b backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-3 px-4 sm:gap-6">
        <Logo />
        <MainNav items={items} />
        <div className="ml-auto flex shrink-0 items-center gap-2">
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
