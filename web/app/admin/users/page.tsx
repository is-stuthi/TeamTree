import { AdminUsersTable } from "@/components/app/AdminUsersTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";
import { getSession } from "@/lib/auth";

export const metadata = { title: "Users & roles · TeamTREE" };

export default async function AdminUsersPage() {
  const api = await serverApi();
  const [{ data: users = [] }, session] = await Promise.all([api.GET("/admin/users"), getSession()]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Users</CardTitle>
        <CardDescription>
          Role changes apply to the API immediately. Deactivation is a soft delete: history is kept.
        </CardDescription>
      </CardHeader>
      <CardContent><AdminUsersTable users={users} currentUserId={session?.userId ?? 0} /></CardContent>
    </Card>
  );
}
