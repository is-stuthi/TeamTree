import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { DashboardSearch } from "@/components/app/DashboardSearch";
import { ProjectCard, ProjectGrid } from "@/components/app/ProjectCard";
import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { serverApi } from "@/lib/api/server";
import { DASHBOARDS } from "@/specs/dashboards";

export const metadata = { title: "Dashboard · TeamTREE" };

export default async function DashboardPage() {
  const api = await serverApi();
  const { data: recommended = [] } = await api.GET("/users/me/recommended-projects");

  return (
    <div className="space-y-8">
      <DashboardSearch />
      {/* Stats on the left (stacked), recommendations on the right; one column on small screens. */}
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <div className="lg:[&_.viz-root]:grid-cols-1">
          <SchemaDashboard spec={DASHBOARDS.my_dashboard} />
        </div>
        <section className="space-y-3">
          <div className="flex items-end justify-between gap-2">
            <div>
              <h2 className="text-lg font-semibold">Recommended for you</h2>
              <p className="text-muted-foreground text-sm">Open projects where you meet at least one requirement.</p>
            </div>
            <Link href="/projects?status=Open" className="text-primary inline-flex shrink-0 items-center gap-1 text-sm font-medium hover:underline">
              Browse all <ArrowRight className="size-4" aria-hidden />
            </Link>
          </div>
          <ProjectGrid empty="Add skills to your profile to get recommendations." className="lg:grid-cols-2">
            {recommended.slice(0, 4).map((p) => (
              <ProjectCard key={p.p_id} project={p} note={`${p.matched_requirements}/${p.total_requirements} requirements met`} />
            ))}
          </ProjectGrid>
        </section>
      </div>
      <SchemaDashboard spec={DASHBOARDS.my_charts} />
    </div>
  );
}
