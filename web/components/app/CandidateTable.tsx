import { CircleCheckIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { components } from "@/lib/api/schema";

type Candidate = components["schemas"]["CandidateOut"];

const FACTORS: { key: keyof Candidate["breakdown"]; label: string; max: number }[] = [
  { key: "coverage", label: "Coverage", max: 50 },
  { key: "proficiency", label: "Proficiency", max: 20 },
  { key: "experience", label: "Experience", max: 15 },
  { key: "domain", label: "Domain", max: 10 },
  { key: "availability", label: "Availability", max: 5 },
];

/** Ranked candidates. Score is a meter (single value vs 100); the five factor
 *  points are printed so the score is explainable, never a black box. */
export function CandidateTable({ candidates }: { candidates: Candidate[] }) {
  if (candidates.length === 0) {
    return <p className="text-muted-foreground text-sm">No eligible candidates. Try showing partial matches.</p>;
  }
  return (
    <div className="viz-root">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Candidate</TableHead><TableHead className="w-48">Score</TableHead>
            <TableHead>Breakdown (points)</TableHead><TableHead>Missing or below level</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {candidates.map((c) => (
            <TableRow key={c.u_id}>
              <TableCell>
                <div className="flex items-center gap-1.5 font-medium">
                  {c.name}
                  {c.fully_qualified && <CircleCheckIcon className="size-4" style={{ color: "var(--viz-status-good)" }} aria-label="Fully qualified" />}
                </div>
                <div className="text-muted-foreground text-xs">{c.experience_level} · {c.availability}</div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className="h-2 flex-1 rounded-full" style={{ background: "var(--viz-track)" }}
                       role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={c.score} aria-label={`Score ${c.score} of 100`}>
                    <div className="h-2 rounded-full" style={{ width: `${c.score}%`, background: "var(--viz-fill)" }} />
                  </div>
                  <span className="w-10 text-right font-medium tabular-nums">{c.score}</span>
                </div>
              </TableCell>
              <TableCell className="text-muted-foreground text-xs">
                <div className="grid grid-cols-5 gap-2">
                  {FACTORS.map((f) => (
                    <div key={f.key} title={`${f.label}: ${c.breakdown[f.key]} of ${f.max}`}>
                      <div>{f.label}</div>
                      <div className="text-foreground tabular-nums">{c.breakdown[f.key]}/{f.max}</div>
                    </div>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {c.missing_skills.length === 0 ? <span className="text-muted-foreground text-xs">None</span>
                    : c.missing_skills.map((s) => <Badge key={s} variant="outline">{s}</Badge>)}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
