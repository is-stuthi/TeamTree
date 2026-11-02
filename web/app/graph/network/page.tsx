import Link from "next/link";
import { redirect } from "next/navigation";
import { NetworkGraph } from "@/components/graph/NetworkGraph";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getMe, serverApi } from "@/lib/api/server";

export const metadata = { title: "My network · TeamTREE" };

export default async function NetworkPage() {
  const me = await getMe();
  if (!me) redirect("/login?next=/graph/network");
  const api = await serverApi();
  const [{ data: network, error }, { data: recs = [] }] = await Promise.all([
    api.GET("/graph/users/{uid}/network", { params: { path: { uid: me.id }, query: { depth: 2 } } }),
    api.GET("/graph/users/{uid}/recommended-collaborators", { params: { path: { uid: me.id } } }),
  ]);
  if (!network) return <p className="text-muted-foreground text-sm">The graph is unavailable right now ({JSON.stringify(error)}).</p>;
  const people = network.nodes.filter((n) => n.degree > 0);

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Collaboration network</CardTitle>
          <CardDescription>People you&apos;ve shared a team with, and theirs. Click a person to open their profile.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {people.length === 0 ? <p className="text-muted-foreground text-sm">Join a team to start building your network.</p>
            : <NetworkGraph network={network} />}
          {people.length > 0 && (
            <ul className="text-sm" aria-label="People in your network">
              {people.map((p) => (
                <li key={p.id} className="flex justify-between border-b py-1 last:border-0">
                  <Link href={`/users/${p.id}`} className="hover:underline">{p.name}</Link>
                  <span className="text-muted-foreground">{p.degree === 1 ? "Collaborator" : "2nd degree"}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
      <Card className="self-start">
        <CardHeader>
          <CardTitle>Recommended collaborators</CardTitle>
          <CardDescription>Collaborators of your collaborators, ranked by mutual connections.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {recs.length === 0 ? <p className="text-muted-foreground text-sm">No recommendations yet.</p> : recs.map((r) => (
            <div key={r.id} className="space-y-1">
              <div className="flex justify-between text-sm">
                <Link href={`/users/${r.id}`} className="font-medium hover:underline">{r.name}</Link>
                <span className="text-muted-foreground">{r.mutual} mutual</span>
              </div>
              <div className="flex flex-wrap gap-1">{r.complementary_skills.map((s) => <Badge key={s} variant="outline">{s}</Badge>)}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
