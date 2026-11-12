import { PageHeader } from "@/components/app/PageHeader";
import { ProjectCard, ProjectGrid } from "@/components/app/ProjectCard";
import { Card, CardContent } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Projects · TeamTREE" };

const STATUSES = ["Open", "Ongoing", "Completed", "Closed"] as const;
type Search = { q?: string; domain?: string; skill?: string; status?: string; deadline_before?: string };

// Bad URL params are dropped instead of turning into a 422 that renders as "no results".
function cleanQuery(sp: Search) {
  const skill = Number(sp.skill);
  return {
    q: sp.q || undefined,
    domain: sp.domain || undefined,
    skill: Number.isInteger(skill) && skill > 0 ? skill : undefined,
    status: STATUSES.find((s) => s === sp.status),
    deadline_before: /^\d{4}-\d{2}-\d{2}$/.test(sp.deadline_before ?? "") ? sp.deadline_before : undefined,
  };
}

export default async function ProjectsPage({ searchParams }: { searchParams: Promise<Search> }) {
  const sp = await searchParams;
  const api = await serverApi();
  const query = cleanQuery(sp);
  const [{ data: projects = [] }, filterSpec] = await Promise.all([
    api.GET("/projects", { params: { query } }), getSpec("project_filter"),
  ]);

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <PageHeader eyebrow="Explore" title="Projects" description="Open projects come first. Filter by skill to find where you fit." />
      <Card>
        <CardContent className="[&_form]:grid-cols-1 [&_form]:sm:grid-cols-2 [&_form]:lg:grid-cols-5 [&_form]:items-end">
          <SchemaForm key={JSON.stringify(sp)} spec={filterSpec} defaultValues={sp} />
        </CardContent>
      </Card>
      <p className="text-muted-foreground text-sm">{projects.length} project{projects.length === 1 ? "" : "s"}</p>
      <ProjectGrid empty="No projects match these filters.">
        {projects.map((p) => <ProjectCard key={p.p_id} project={p} />)}
      </ProjectGrid>
    </div>
  );
}
