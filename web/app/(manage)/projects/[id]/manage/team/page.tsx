import { SpecDialog } from "@/components/app/SpecDialog";
import { TeamTable } from "@/components/app/TeamTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Team · TeamTREE" };

export default async function TeamPage({ params }: { params: Promise<{ id: string }> }) {
  const p_id = Number((await params).id);
  const api = await serverApi();
  const [{ data: members = [] }, { data: top = [] }, transferSpec] = await Promise.all([
    api.GET("/projects/{p_id}/team", { params: { path: { p_id }, query: { include_past: true } } }),
    api.GET("/projects/{p_id}/team/top-contributors", { params: { path: { p_id } } }),
    getSpec("transfer_ownership"),
  ]);

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle>Team</CardTitle>
              <CardDescription>Past members stay listed so contribution history is preserved.</CardDescription>
            </div>
            <SpecDialog spec={transferSpec} trigger="Transfer ownership" variant="outline" size="sm"
                        params={{ p_id }} description="The new owner must be an active member of this team." />
          </div>
        </CardHeader>
        <CardContent><TeamTable members={members} manageFor={p_id} /></CardContent>
      </Card>
      <Card className="self-start">
        <CardHeader>
          <CardTitle>Top contributors</CardTitle>
          <CardDescription>Members above the team&apos;s average of completed tasks (correlated query).</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {top.length === 0 ? <p className="text-muted-foreground">Nobody is above the average yet.</p> : top.map((t) => (
            <div key={t.u_id} className="flex justify-between"><span>{t.member_name}</span><span className="tabular-nums">{t.done} done</span></div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
