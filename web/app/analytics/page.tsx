import Link from "next/link";
import { redirect } from "next/navigation";
import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { buttonVariants } from "@/components/ui/button";
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
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground text-sm">Every number comes from a SQL view or query; nothing is computed in the browser.</p>
      </div>
      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Analytics section">
        {tabs.map((t) => (
          <Link key={t.key} href={`?tab=${t.key}`} role="tab" aria-selected={t.key === active.key}
                className={buttonVariants({ size: "sm", variant: t.key === active.key ? "default" : "outline" })}>
            {t.label}
          </Link>
        ))}
      </div>
      {active.spec.description && <p className="text-muted-foreground text-sm">{active.spec.description}</p>}
      <SchemaDashboard spec={active.spec} />
    </main>
  );
}
