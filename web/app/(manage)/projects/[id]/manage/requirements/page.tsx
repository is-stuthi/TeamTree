import { RequirementsTable } from "@/components/app/RequirementsTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Requirements · TeamTREE" };

export default async function RequirementsPage({ params }: { params: Promise<{ id: string }> }) {
  const p_id = Number((await params).id);
  const api = await serverApi();
  const [{ data: requirements = [] }, addSpec, copySpec] = await Promise.all([
    api.GET("/projects/{p_id}/requirements", { params: { path: { p_id } } }),
    getSpec("requirement_add"), getSpec("requirement_copy"),
  ]);

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Skill requirements</CardTitle>
          <CardDescription>Matching and the skill-gap report compare these with your team and applicants.</CardDescription>
        </CardHeader>
        <CardContent><RequirementsTable requirements={requirements} editableFor={p_id} /></CardContent>
      </Card>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>{addSpec.title}</CardTitle>
            <CardDescription>Same skill + role updates the level and count.</CardDescription>
          </CardHeader>
          <CardContent><SchemaForm spec={addSpec} params={{ p_id }} resetOnSuccess /></CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{copySpec.title}</CardTitle>
            <CardDescription>Use another project as a template (INSERT … SELECT).</CardDescription>
          </CardHeader>
          <CardContent><SchemaForm spec={copySpec} params={{ p_id }} resetOnSuccess /></CardContent>
        </Card>
      </div>
    </div>
  );
}
