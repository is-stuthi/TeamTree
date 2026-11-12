import { ProjectCard, ProjectGrid } from "@/components/app/ProjectCard";
import { SpecDialog } from "@/components/app/SpecDialog";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "My projects · TeamTREE" };

// Projects you own. Teams you joined live on /dashboard/teams; suggestions on the dashboard.
export default async function MyProjectsPage() {
  const api = await serverApi();
  const [{ data: mine = [] }, createSpec] = await Promise.all([api.GET("/users/me/projects"), getSpec("project_create")]);
  const owned = mine.filter((p) => p.is_owner);

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-muted-foreground text-sm">{owned.length} project{owned.length === 1 ? "" : "s"}</p>
        <SpecDialog spec={createSpec} trigger="New project"
                    description="You become the owner and the first member of its team." />
      </div>
      <ProjectGrid empty="You don't own any projects yet. Create one to start building a team.">
        {owned.map((p) => <ProjectCard key={p.p_id} project={p} />)}
      </ProjectGrid>
    </section>
  );
}
