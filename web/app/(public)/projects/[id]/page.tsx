import { notFound } from "next/navigation";
import { ProjectActions } from "@/components/app/ProjectActions";
import { RequirementsTable } from "@/components/app/RequirementsTable";
import { OverdueBadge, StatusBadge } from "@/components/app/StatusBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSpec, serverApi } from "@/lib/api/server";
import { getSession } from "@/lib/auth";

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const api = await serverApi();
  const [{ data: p }, session, applySpec] = await Promise.all([
    api.GET("/projects/{p_id}", { params: { path: { p_id: Number(id) } } }), getSession(), getSpec("application_create"),
  ]);
  if (!p) notFound();
  const capacity = p.max_team_size ? `${p.team_size} / ${p.max_team_size}` : `${p.team_size} (no limit)`;

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2"><StatusBadge status={p.status} /><OverdueBadge overdue={p.is_overdue} /></div>
          <h1 className="text-3xl font-semibold tracking-tight">{p.p_name}</h1>
          <div className="flex flex-wrap gap-1.5">{p.domains.map((d) => <Badge key={d} variant="outline">{d}</Badge>)}</div>
        </div>
        <ProjectActions project={p} loggedIn={Boolean(session)} applySpec={applySpec} />
      </div>
      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>About</CardTitle></CardHeader>
            <CardContent><p className="whitespace-pre-line text-sm">{p.description || "No description yet."}</p></CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Skills needed</CardTitle>
              <CardDescription>Minimum proficiency and number of people per role.</CardDescription>
            </CardHeader>
            <CardContent><RequirementsTable requirements={p.requirements} /></CardContent>
          </Card>
        </div>
        <Card className="self-start">
          <CardHeader><CardTitle>Details</CardTitle></CardHeader>
          <CardContent className="grid gap-3 text-sm">
            <Detail label="Owner" value={p.owner_name} sub={p.owner_bio} />
            <Detail label="Team" value={`${p.team_name}: ${capacity}`} />
            <Detail label="Deadline" value={p.deadline ?? "None"} />
            <Detail label="Created" value={new Date(p.creation_date).toLocaleDateString()} />
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

function Detail({ label, value, sub }: { label: string; value: string; sub?: string | null }) {
  return (
    <div>
      <div className="text-muted-foreground text-xs">{label}</div>
      <div className="font-medium">{value}</div>
      {sub && <div className="text-muted-foreground text-xs">{sub}</div>}
    </div>
  );
}
