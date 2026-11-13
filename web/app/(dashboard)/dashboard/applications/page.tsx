import Link from "next/link";
import { RowActions } from "@/components/app/RowActions";
import { StatusBadge } from "@/components/app/StatusBadge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { serverApi } from "@/lib/api/server";

export const metadata = { title: "My applications · TeamTREE" };

const date = (d?: string | null) => (d ? new Date(d).toLocaleDateString() : "—");

export default async function MyApplicationsPage() {
  const api = await serverApi();
  const { data: apps = [] } = await api.GET("/users/me/applications");

  return (
    <Card>
      <CardHeader>
        <CardTitle>My applications</CardTitle>
        <CardDescription>You can reapply to a project after a rejection or withdrawal.</CardDescription>
      </CardHeader>
      <CardContent>
        {apps.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            No applications yet. <Link href="/projects" className="underline">Browse projects</Link>.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow><TableHead>Project</TableHead><TableHead>Status</TableHead><TableHead>Applied</TableHead><TableHead>Decided</TableHead><TableHead /></TableRow>
            </TableHeader>
            <TableBody>
              {apps.map((a) => (
                <TableRow key={a.a_id}>
                  <TableCell className="font-medium"><Link href={`/projects/${a.p_id}`} className="hover:underline">{a.p_name}</Link></TableCell>
                  <TableCell><StatusBadge status={a.status} /></TableCell>
                  <TableCell>{date(a.a_date)}</TableCell>
                  <TableCell>{date(a.decision_date)}</TableCell>
                  <TableCell className="w-10 text-right">
                    <RowActions label={`Actions for ${a.p_name}`} actions={[
                      { label: "Open project", icon: "open", href: `/projects/${a.p_id}` },
                      ...(a.status === "Pending"
                        ? [{ label: "Withdraw application", icon: "withdraw" as const, destructive: true, method: "POST" as const,
                             path: `/applications/${a.a_id}/withdraw`, success: "Application withdrawn",
                             confirm: `Your application to ${a.p_name} will be withdrawn. You can apply again later.` }]
                        : []),
                    ]} />
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
