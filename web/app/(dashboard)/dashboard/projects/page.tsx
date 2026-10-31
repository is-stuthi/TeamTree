import { ProjectCard, ProjectGrid } from "@/components/app/ProjectCard";
import { SpecDialog } from "@/components/app/SpecDialog";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "My projects · TeamTREE" };

export default async function MyProjectsPage() {
  const api = await serverApi();
  const [{ data: mine = [] }, { data: recommended = [] }, createSpec] = await Promise.all([
    api.GET("/users/me/projects"), api.GET("/users/me/recommended-projects"), getSpec("project_create"),
  ]);
  const owned = mine.filter((p) => p.is_owner);
  const member = mine.filter((p) => !p.is_owner);

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">Projects I own</h2>
          <SpecDialog spec={createSpec} trigger="New project"
                      description="You become the owner and the first member of its team." />
        </div>
        <ProjectGrid empty="You don't own any projects yet.">
          {owned.map((p) => <ProjectCard key={p.p_id} project={p} />)}
        </ProjectGrid>
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Teams I&apos;m on</h2>
        <ProjectGrid empty="Not on any other team yet. Apply to a project below.">
          {member.map((p) => <ProjectCard key={p.p_id} project={p} note={`Role: ${p.my_role}`} />)}
        </ProjectGrid>
      </section>
      <section className="space-y-3">
        <div>
          <h2 className="text-lg font-semibold">Recommended for you</h2>
          <p className="text-muted-foreground text-sm">Open projects where you meet at least one requirement.</p>
        </div>
        <ProjectGrid empty="Add skills to your profile to get recommendations.">
          {recommended.map((p) => (
            <ProjectCard key={p.p_id} project={p} note={`${p.matched_requirements}/${p.total_requirements} requirements met`} />
          ))}
        </ProjectGrid>
      </section>
    </div>
  );
}
