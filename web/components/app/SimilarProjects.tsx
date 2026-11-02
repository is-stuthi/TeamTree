import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";

/** Vector-similar projects (Neo4j project_embedding index). Hidden if the graph is down. */
export async function SimilarProjects({ projectId }: { projectId: number }) {
  const api = await serverApi();
  const { data = [] } = await api.GET("/graph/projects/{pid}/similar", { params: { path: { pid: projectId } } });
  if (data.length === 0) return null;
  return (
    <Card className="self-start">
      <CardHeader>
        <CardTitle>Similar projects</CardTitle>
        <CardDescription>By meaning of name, description, domains and skills.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {data.map((p) => (
          <div key={p.id} className="flex justify-between gap-2">
            <Link href={`/projects/${p.id}`} className="hover:underline">{p.name}</Link>
            <span className="text-muted-foreground tabular-nums">{p.score.toFixed(2)}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
