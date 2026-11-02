import { TaskTable } from "@/components/app/TaskTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";

export const metadata = { title: "My tasks · TeamTREE" };

export default async function MyTasksPage() {
  const api = await serverApi();
  const { data: tasks = [] } = await api.GET("/users/me/tasks");
  const overdue = tasks.filter((t) => t.is_overdue).length;

  return (
    <Card>
      <CardHeader>
        <CardTitle>My tasks</CardTitle>
        <CardDescription>
          {tasks.length} assigned{overdue > 0 && `, ${overdue} overdue`}. Update status as you go; the owner sees it immediately.
        </CardDescription>
      </CardHeader>
      <CardContent><TaskTable tasks={tasks} showProject /></CardContent>
    </Card>
  );
}
