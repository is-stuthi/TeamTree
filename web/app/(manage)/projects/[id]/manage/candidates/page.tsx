import Link from "next/link";
import { CandidateTable } from "@/components/app/CandidateTable";
import { GapSuggestions } from "@/components/app/GapSuggestions";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { serverApi } from "@/lib/api/server";

export const metadata = { title: "Candidates · TeamTREE" };

export default async function CandidatesPage({ params, searchParams }: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ full?: string }>;
}) {
  const p_id = Number((await params).id);
  const full = (await searchParams).full === "1";
  const api = await serverApi();
  const { data: candidates = [] } = await api.GET("/projects/{p_id}/candidates", {
    params: { path: { p_id }, query: { full, limit: 30 } },
  });

  return (
    <div className="space-y-6">
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <CardTitle>Candidates</CardTitle>
            <CardDescription>
              Ranked by an <strong>indicative</strong> score: coverage 50, proficiency 20, experience 15,
              domain 10, availability 5. Members, the owner and pending applicants are excluded.
            </CardDescription>
          </div>
          <div className="flex gap-2" role="tablist" aria-label="Candidate filter">
            <Link href="?full=0" role="tab" aria-selected={!full} className={buttonVariants({ size: "sm", variant: full ? "outline" : "default" })}>
              Any required skill
            </Link>
            <Link href="?full=1" role="tab" aria-selected={full} className={buttonVariants({ size: "sm", variant: full ? "default" : "outline" })}>
              Fully qualified only
            </Link>
          </div>
        </div>
      </CardHeader>
      <CardContent><CandidateTable candidates={candidates} /></CardContent>
    </Card>
    <GapSuggestions projectId={p_id} />
    </div>
  );
}
