import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";

/** Graph suggestions for the skill gap: MySQL SkillGap shortfalls x Neo4j HAS_SKILL /
 *  RELATED_TO / ENDORSES. Hidden when there is no gap or the graph is unavailable. */
export async function GapSuggestions({ projectId }: { projectId: number }) {
  const api = await serverApi();
  const { data = [] } = await api.GET("/graph/projects/{pid}/gap-candidates", { params: { path: { pid: projectId } } });
  if (data.length === 0) return null;
  const bySkill = Object.groupBy(data, (r) => r.skill);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Graph suggestions for your skill gap</CardTitle>
        <CardDescription>People who have a missing skill, or a related one, ranked by endorsements.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2">
        {Object.entries(bySkill).map(([skill, rows]) => (
          <div key={skill} className="space-y-1">
            <div className="text-sm font-medium">Missing: {skill}</div>
            {(rows ?? []).slice(0, 6).map((r) => (
              <div key={`${r.user_id}-${r.via}`} className="flex items-center justify-between gap-2 text-sm">
                <Link href={`/users/${r.user_id}`} className="hover:underline">{r.name}</Link>
                <span className="flex items-center gap-1.5">
                  <Badge variant={r.related ? "outline" : "secondary"}>{r.related ? `related: ${r.via}` : r.via}</Badge>
                  {r.endorsements > 0 && <span className="text-muted-foreground text-xs tabular-nums">★ {r.endorsements.toFixed(1)}</span>}
                </span>
              </div>
            ))}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
