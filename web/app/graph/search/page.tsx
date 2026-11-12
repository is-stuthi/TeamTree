import Link from "next/link";
import { redirect } from "next/navigation";
import { GraphUnavailable } from "@/components/app/GraphUnavailable";
import { PageHeader } from "@/components/app/PageHeader";
import { Card, CardContent } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";

export const metadata = { title: "Search by meaning · TeamTREE" };

// Results page for the dashboard search bar's "By meaning" button (Neo4j vector index).
// Not in the sidebar: the query is typed on the dashboard.
export default async function SearchPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const q = ((await searchParams).q ?? "").trim();
  if (q.length < 2) redirect("/dashboard");
  const results = await (await serverApi()).GET("/graph/search/projects", { params: { query: { q } } });
  const rows = results.data ?? [];

  return (
    <div className="space-y-6">
      <PageHeader title={<>Results for “{q}”</>}
                  description="Open projects ranked by cosine similarity between your text and each project's embedding." />
      <Card>
        <CardContent>
          {results.error ? <GraphUnavailable what="Semantic search results" />
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
    </div>
  );
}
