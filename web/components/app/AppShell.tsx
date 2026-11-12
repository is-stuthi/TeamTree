import { cookies } from "next/headers";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { getMe } from "@/lib/api/server";
import { AppBreadcrumb } from "./AppBreadcrumb";
import { AppSidebar } from "./AppSidebar";
import { SiteHeader } from "./SiteHeader";
import { UserMenu } from "./UserMenu";

/**
 * Signed in: sidebar + top bar (trigger, breadcrumb, account) around every page.
 * Guests: the simple marketing header.
 */
export async function AppShell({ children }: { children: React.ReactNode }) {
  const me = await getMe();          // live role, so promotions show without re-login
  if (!me) {
    return (
      <>
        <SiteHeader />
        <main>{children}</main>
      </>
    );
  }

  const defaultOpen = (await cookies()).get("sidebar_state")?.value !== "false";
  return (
    <SidebarProvider defaultOpen={defaultOpen}>
      <AppSidebar isAdmin={me.role === "admin"} />
      <SidebarInset>
        <header className="bg-background/80 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-30 flex h-14 shrink-0 items-center gap-2 border-b px-4 backdrop-blur">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-1 data-vertical:h-4 data-vertical:self-center" />
          <AppBreadcrumb />
          <div className="ml-auto">
            <UserMenu name={`${me.f_name} ${me.l_name}`} role={me.role} />
          </div>
        </header>
        <div className="flex-1">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
