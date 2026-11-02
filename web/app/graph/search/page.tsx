import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Semantic search · TeamTREE" };

export default async function SearchPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const q = ((await searchParams).q ?? "").trim();
  const api = await serverApi();
  const [spec, results] = await Promise.all([
    getSpec("graph_search"),
    q.length >= 2 ? api.GET("/graph/search/projects", { params: { query: { q } } }) : Promise.resolve(null),
  ]);
  const rows = results?.data ?? [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{spec.title}</CardTitle>
          <CardDescription>Open projects ranked by cosine similarity between your text and each project&apos;s embedding.</CardDescription>
        </CardHeader>
        <CardContent><SchemaForm key={q} spec={spec} defaultValues={{ q }} /></CardContent>
      </Card>
      {q && (
        <Card>
          <CardHeader><CardTitle>Results for “{q}”</CardTitle></CardHeader>
          <CardContent>
            {results?.error ? <p className="text-muted-foreground text-sm">Search is unavailable right now.</p>
              : rows.length === 0 ? <p className="text-muted-foreground text-sm">No open projects matched.</p> : (
              <ol className="space-y-2">
                {rows.map((r, i) => (
                  <li key={r.id} className="flex items-baseline justify-between gap-4 border-b pb-2 last:border-0">
                    <span><span className="text-muted-foreground mr-2 tabular-nums">{i + 1}.</span>
                      <Link href={`/projects/${r.id}`} className="font-medium hover:underline">{r.name}</Link></span>
                    <span className="text-muted-foreground text-sm tabular-nums">similarity {r.score.toFixed(2)}</span>
                  </li>
                ))}
              </ol>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
