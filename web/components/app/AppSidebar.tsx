"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NetworkIcon } from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel,
  SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail, useSidebar,
} from "@/components/ui/sidebar";
import { activeNav, navFor } from "./nav";

/** Global app navigation, grouped by intent. Collapses to icons; a sheet on phones. */
export function AppSidebar({ isAdmin, footer }: { isAdmin: boolean; footer?: React.ReactNode }) {
  const pathname = usePathname();
  const { setOpenMobile } = useSidebar();
  const current = activeNav(pathname)?.item.href;

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" tooltip="TeamTREE" render={<Link href="/dashboard" onClick={() => setOpenMobile(false)} />}>
              <span className="bg-primary text-primary-foreground flex size-8 shrink-0 items-center justify-center rounded-lg">
                <NetworkIcon className="size-4" aria-hidden />
              </span>
              <span className="flex flex-col leading-tight">
                <span className="font-semibold tracking-tight">Team<span className="text-primary">TREE</span></span>
                <span className="text-muted-foreground text-xs">Skill-based teams</span>
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {navFor(isAdmin).map((group) => (
          <SidebarGroup key={group.label}>
            <SidebarGroupLabel>{group.label}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      isActive={item.href === current}
                      tooltip={item.label}
                      render={<Link href={item.href} aria-current={item.href === current ? "page" : undefined} onClick={() => setOpenMobile(false)} />}
                    >
                      <item.icon aria-hidden />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>

      {footer && <SidebarFooter>{footer}</SidebarFooter>}
      <SidebarRail />
    </Sidebar>
  );
}
