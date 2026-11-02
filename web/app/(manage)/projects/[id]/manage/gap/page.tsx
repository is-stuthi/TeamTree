import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import type { DashboardSpec } from "@/components/schema/dashboard";
import spec from "@/specs/dashboards/skill_gap.json";

export const metadata = { title: "Skill gap · TeamTREE" };

export default async function SkillGapPage({ params }: { params: Promise<{ id: string }> }) {
  const id = Number((await params).id);
  return (
    <div className="space-y-2">
      <p className="text-muted-foreground text-sm">{spec.description}</p>
      <SchemaDashboard spec={spec as DashboardSpec} params={{ id }} />
    </div>
  );
}
