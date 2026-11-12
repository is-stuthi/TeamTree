import { PageHeader } from "@/components/app/PageHeader";
import Link from "next/link";
import { redirect } from "next/navigation";
import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { cn } from "@/lib/utils";
import { getMe } from "@/lib/api/server";
import { ANALYTICS_TABS } from "@/specs/dashboards";

export const metadata = { title: "Analytics · TeamTREE" };

// Members see Skills/Projects/Applications; admins also see Users/Teams
// (the API enforces this too: /analytics/users and /analytics/teams are admin-only).
export default async function AnalyticsPage({ searchParams }: { searchParams: Promise<{ tab?: string }> }) {
  const me = await getMe();
  if (!me) redirect("/login?next=/analytics");
  const tabs = ANALYTICS_TABS.filter((t) => !t.adminOnly || me.role === "admin");
  const requested = (await searchParams).tab;
  const active = tabs.find((t) => t.key === requested) ?? tabs[0];

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <PageHeader title="Analytics" description="Every number comes from a SQL view or query; nothing is computed in the browser." />
      <div className="no-scrollbar bg-muted/70 flex w-fit max-w-full gap-1 overflow-x-auto rounded-xl border p-1" role="tablist" aria-label="Analytics section">
        {tabs.map((t) => (
          <Link key={t.key} href={`?tab=${t.key}`} role="tab" aria-selected={t.key === active.key}
                className={cn("rounded-lg px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-all",
                  t.key === active.key ? "bg-background text-foreground shadow-sm ring-1 ring-border" : "text-muted-foreground hover:text-foreground")}>
            {t.label}
          </Link>
        ))}
      </div>
      {active.spec.description && <p className="text-muted-foreground text-sm">{active.spec.description}</p>}
      <SchemaDashboard spec={active.spec} />
    </div>
  );
}
