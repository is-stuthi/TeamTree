import { ActionButton } from "@/components/app/ActionButton";
import { AdminUsersTable } from "@/components/app/AdminUsersTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";
import { getSession } from "@/lib/auth";

export const metadata = { title: "Users & roles · TeamTREE" };

export default async function AdminUsersPage() {
  const api = await serverApi();
  const [{ data: users = [] }, session] = await Promise.all([api.GET("/admin/users"), getSession()]);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>
            Role changes apply to the API immediately. Deactivation is a soft delete: history is kept.
          </CardDescription>
        </CardHeader>
        <CardContent><AdminUsersTable users={users} currentUserId={session?.userId ?? 0} /></CardContent>
      </Card>
      {/* Dev only: hidden in production builds, and the API refuses it unless APP_ENV=development. */}
      {process.env.NODE_ENV !== "production" && (
        <Card className="border-destructive/40">
          <CardHeader>
            <CardTitle>Reset demo data</CardTitle>
            <CardDescription>
              Development only. Re-applies the schema and seed to MySQL and rebuilds the Neo4j graph.
              Everything created since the last reset is lost.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ActionButton label="Reset seed data" method="POST" path="/admin/dev/reset" variant="destructive"
              success="Demo data reloaded." confirm="Wipe all data and reload the demo seed?" />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
