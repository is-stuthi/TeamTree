import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getProject, getSpec } from "@/lib/api/server";

export const metadata = { title: "Project settings · TeamTREE" };

export default async function ProjectSettingsPage({ params }: { params: Promise<{ id: string }> }) {
  const p_id = Number((await params).id);
  const [p, spec] = await Promise.all([getProject(p_id), getSpec("project_edit")]);   // shared with layout
  if (!p) return null;

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle>{spec.title}</CardTitle>
        <CardDescription>
          Ownership can only change through a transfer (P4). The database blocks direct edits to the owner column.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <SchemaForm spec={spec} params={{ p_id }} defaultValues={p} />
      </CardContent>
    </Card>
  );
}
