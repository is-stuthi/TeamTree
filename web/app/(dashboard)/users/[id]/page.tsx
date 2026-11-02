import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { EndorsementList } from "@/components/app/EndorsementList";
import { SpecDialog } from "@/components/app/SpecDialog";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getMe, getSpec, serverApi } from "@/lib/api/server";

export default async function UserPage({ params }: { params: Promise<{ id: string }> }) {
  const uid = Number((await params).id);
  const me = await getMe();
  if (!me) redirect(`/login?next=/users/${uid}`);
  const api = await serverApi();
  const self = me.id === uid;
  const [{ data: user }, { data: endorsements = [] }, { data: similar = [] }, path, endorseSpec] = await Promise.all([
    api.GET("/users/{user_id}", { params: { path: { user_id: uid } } }),
    api.GET("/graph/users/{uid}/endorsements", { params: { path: { uid } } }),
    api.GET("/graph/users/{uid}/similar", { params: { path: { uid } } }),
    self ? Promise.resolve(null) : api.GET("/graph/path", { params: { query: { from: me.id, to: uid } } }),
    getSpec("endorse"),
  ]);
  if (!user) notFound();
  const route = path?.data;

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">{user.name}</h1>
          <p className="text-muted-foreground text-sm">
            {user.experience_level} · {user.availability}{user.location && ` · ${user.location}`}
            {user.strongest_skill && <> · strongest skill: <span className="text-foreground">{user.strongest_skill}</span></>}
          </p>
        </div>
        {!self && <SpecDialog spec={endorseSpec} trigger="Endorse" params={{ to: uid }} defaultValues={{ to: uid }}
                              description="Only people you've shared a team with can be endorsed." />}
      </div>
      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          {user.bio && <Card><CardContent className="pt-6 text-sm">{user.bio}</CardContent></Card>}
          <Card>
            <CardHeader><CardTitle>Skills</CardTitle></CardHeader>
            <CardContent className="flex flex-wrap gap-1.5">
              {user.skills.map((s) => <Badge key={s.s_id} variant="secondary">{s.s_name} · {s.u_s_level}</Badge>)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Endorsements</CardTitle>
              <CardDescription>Stored in the graph (ENDORSES relationships), not in MySQL.</CardDescription>
            </CardHeader>
            <CardContent><EndorsementList endorsements={endorsements} profileId={uid} myId={me.id} /></CardContent>
          </Card>
        </div>
        <div className="space-y-6">
          {!self && (
            <Card>
              <CardHeader><CardTitle>How you&apos;re connected</CardTitle></CardHeader>
              <CardContent className="text-sm">
                {route?.hops ? <p>{route.path.map((n) => n.name).join(" → ")} <span className="text-muted-foreground">({route.hops} hop{route.hops > 1 ? "s" : ""})</span></p>
                  : <p className="text-muted-foreground">No collaboration path yet.</p>}
              </CardContent>
            </Card>
          )}
          <Card>
            <CardHeader><CardTitle>Similar people</CardTitle><CardDescription>By profile embedding.</CardDescription></CardHeader>
            <CardContent className="space-y-1 text-sm">
              {similar.map((s) => <div key={s.id}><Link href={`/users/${s.id}`} className="hover:underline">{s.name}</Link></div>)}
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
