import Link from "next/link";
import { ActionButton } from "@/components/app/ActionButton";
import { StatusBadge } from "@/components/app/StatusBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { serverApi } from "@/lib/api/server";

export const metadata = { title: "My teams · TeamTREE" };

export default async function MyTeamsPage() {
  const api = await serverApi();
  const { data: teams = [] } = await api.GET("/users/me/teams");

  return (
    <Card>
      <CardHeader>
        <CardTitle>My teams</CardTitle>
        <CardDescription>Owners must transfer ownership before leaving a team.</CardDescription>
      </CardHeader>
      <CardContent>
        {teams.length === 0 ? <p className="text-muted-foreground text-sm">You&apos;re not on any team yet.</p> : (
          <Table>
            <TableHeader>
              <TableRow><TableHead>Project</TableHead><TableHead>Status</TableHead><TableHead>Role</TableHead><TableHead>Joined</TableHead><TableHead className="text-right">Size</TableHead><TableHead /></TableRow>
            </TableHeader>
            <TableBody>
              {teams.map((t) => (
                <TableRow key={t.p_id}>
                  <TableCell className="font-medium">
                    <Link href={t.is_owner ? `/projects/${t.p_id}/manage/team` : `/projects/${t.p_id}`} className="hover:underline">{t.p_name}</Link>
                  </TableCell>
                  <TableCell><StatusBadge status={t.status} /></TableCell>
                  <TableCell><Badge variant={t.is_owner ? "default" : "secondary"}>{t.role}</Badge></TableCell>
                  <TableCell>{t.join_date}</TableCell>
                  <TableCell className="text-right tabular-nums">{t.team_size}</TableCell>
                  <TableCell className="text-right">
                    {!t.is_owner && (
                      <ActionButton label="Leave" method="POST" path={`/projects/${t.p_id}/team/leave`} success={`You left ${t.p_name}`}
                                    confirm={`Leave ${t.p_name}? Your unfinished tasks become unassigned.`} />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
