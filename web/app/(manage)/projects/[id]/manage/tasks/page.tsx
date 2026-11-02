import { SpecDialog } from "@/components/app/SpecDialog";
import { TaskTable } from "@/components/app/TaskTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Tasks · TeamTREE" };

export default async function TasksPage({ params }: { params: Promise<{ id: string }> }) {
  const p_id = Number((await params).id);
  const api = await serverApi();
  const [{ data: tree = [] }, { data: team = [] }, createSpec] = await Promise.all([
    api.GET("/projects/{p_id}/tasks/tree", { params: { path: { p_id } } }),
    api.GET("/projects/{p_id}/team", { params: { path: { p_id } } }),
    getSpec("task_create"),
  ]);
  const members = team.map((m) => ({ value: String(m.u_id), label: m.member_name }));
  const done = tree.filter((t) => t.status === "Done").length;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle>Tasks</CardTitle>
            <CardDescription>
              {done}/{tree.length} done. Subtasks are shown as a tree (recursive CTE). Only active members can be assigned.
            </CardDescription>
          </div>
          <SpecDialog spec={createSpec} trigger="New task" size="sm" params={{ p_id }} />
        </div>
      </CardHeader>
      <CardContent><TaskTable tasks={tree} members={members} /></CardContent>
    </Card>
  );
}
