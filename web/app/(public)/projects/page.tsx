import { ProjectCard, ProjectGrid } from "@/components/app/ProjectCard";
import { Card, CardContent } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Projects · TeamTREE" };

type Status = "Open" | "Ongoing" | "Completed" | "Closed";
type Search = { q?: string; domain?: string; skill?: string; status?: Status; deadline_before?: string };

export default async function ProjectsPage({ searchParams }: { searchParams: Promise<Search> }) {
  const sp = await searchParams;
  const api = await serverApi();
  const query = { ...sp, skill: sp.skill ? Number(sp.skill) : undefined };
  const [{ data: projects = [] }, filterSpec] = await Promise.all([
    api.GET("/projects", { params: { query } }), getSpec("project_filter"),
  ]);

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
        <p className="text-muted-foreground text-sm">Open projects come first. Filter by skill to find where you fit.</p>
      </div>
      <Card>
        <CardContent className="[&_form]:grid-cols-1 [&_form]:sm:grid-cols-2 [&_form]:lg:grid-cols-5 [&_form]:items-end">
          <SchemaForm key={JSON.stringify(sp)} spec={filterSpec} defaultValues={sp} />
        </CardContent>
      </Card>
      <p className="text-muted-foreground text-sm">{projects.length} project{projects.length === 1 ? "" : "s"}</p>
      <ProjectGrid empty="No projects match these filters.">
        {projects.map((p) => <ProjectCard key={p.p_id} project={p} />)}
      </ProjectGrid>
    </main>
  );
}
