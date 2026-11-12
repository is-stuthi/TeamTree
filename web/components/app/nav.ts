import {
  BarChart3, Compass, History, FolderKanban, Inbox, LayoutDashboard, ListChecks,
  Network, ShieldCheck, Sparkles, Tags, UserRound, Users, type LucideIcon,
} from "lucide-react";

export interface NavLink {
  href: string;
  label: string;
  description: string;
  icon: LucideIcon;
  /** Extra routes that belong to this item (e.g. a project's manage area). */
  also?: RegExp;
}

export interface NavGroup {
  label: string;
  adminOnly?: boolean;
  items: NavLink[];
}

/** Single source of truth for app navigation: sidebar, breadcrumbs and page titles. */
export const NAV: NavGroup[] = [
  {
    label: "Workspace",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, also: /^\/graph\/search/, description: "Search, your numbers and projects picked for you." },
      { href: "/dashboard/activity", label: "Activity", icon: History, description: "Everything you've done recently: applications, team changes and tasks." },
      { href: "/dashboard/projects", label: "My projects", icon: FolderKanban, also: /^\/projects\/\d+\/manage/, description: "Projects you own and run." },
      { href: "/dashboard/applications", label: "Applications", icon: Inbox, description: "Applications you have sent to projects." },
      { href: "/dashboard/teams", label: "Teams", icon: Users, description: "Every team you are on, including your own projects. Owners must transfer ownership before leaving." },
      { href: "/dashboard/tasks", label: "Tasks", icon: ListChecks, description: "Tasks assigned to you." },
    ],
  },
  {
    label: "Discover",
    items: [
      { href: "/projects", label: "Browse projects", icon: Compass, description: "Find open projects that need your skills." },
      { href: "/graph/network", label: "Network", icon: Network, description: "Your collaboration graph, powered by Neo4j." },
      { href: "/analytics", label: "Analytics", icon: BarChart3, description: "Every number comes from a SQL view or query." },
    ],
  },
  {
    label: "Account",
    items: [
      { href: "/dashboard/profile", label: "Profile", icon: UserRound, description: "Your details and password." },
      { href: "/dashboard/skills", label: "My skills", icon: Sparkles, description: "Skills and proficiency levels you have declared." },
    ],
  },
  {
    label: "Admin",
    adminOnly: true,
    items: [
      { href: "/admin/skills", label: "Skill catalogue", icon: Tags, description: "Add, rename and relate skills." },
      { href: "/admin/users", label: "Users & roles", icon: ShieldCheck, description: "Promote, demote and deactivate users." },
    ],
  },
];

export const navFor = (isAdmin: boolean) => NAV.filter((g) => !g.adminOnly || isAdmin);

/** Best nav match for a path: an `also` match wins, then the longest href prefix. */
export function activeNav(pathname: string): { group: NavGroup; item: NavLink } | null {
  let best: { group: NavGroup; item: NavLink; score: number } | null = null;
  for (const group of NAV) {
    for (const item of group.items) {
      const score = item.also?.test(pathname) ? 10_000
        : pathname === item.href || pathname.startsWith(item.href + "/") ? item.href.length : -1;
      if (score >= 0 && (!best || score > best.score)) best = { group, item, score };
    }
  }
  return best && { group: best.group, item: best.item };
}
