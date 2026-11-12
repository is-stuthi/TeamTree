import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { components } from "@/lib/api/schema";
import { cn } from "@/lib/utils";
import { OverdueBadge, StatusBadge } from "./StatusBadge";

type Card_ = components["schemas"]["ProjectCard"];

interface ProjectCardProps {
  project: Card_;
  note?: React.ReactNode;     // e.g. "3/3 requirements matched" or "Your role: Owner"
}

export function ProjectCard({ project: p, note }: ProjectCardProps) {
  const capacity = p.max_team_size ? `${p.team_size}/${p.max_team_size}` : `${p.team_size}`;
  return (
    <Card className="hover:border-primary/40 relative flex flex-col transition-all hover:-translate-y-0.5 hover:shadow-lg">
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="leading-snug">
            {/* stretched link: the whole card is the click target */}
            <Link href={`/projects/${p.p_id}`} className="after:absolute after:inset-0 after:rounded-xl hover:text-primary">{p.p_name}</Link>
          </CardTitle>
          <div className="flex shrink-0 gap-1"><OverdueBadge overdue={p.is_overdue} /><StatusBadge status={p.status} /></div>
        </div>
        <CardDescription className="line-clamp-2">{p.description}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-1.5">
        {p.required_skills.slice(0, 5).map((s) => <Badge key={s} variant="secondary">{s}</Badge>)}
        {p.required_skills.length > 5 && <Badge variant="outline">+{p.required_skills.length - 5}</Badge>}
      </CardContent>
      <CardFooter className="text-muted-foreground mt-auto flex justify-between gap-2 border-t pt-4 text-xs">
        <span>{p.owner_name} · team {capacity}</span>
        <span>{note ?? (p.deadline ? `due ${p.deadline}` : p.domains.join(", "))}</span>
      </CardFooter>
    </Card>
  );
}

export function ProjectGrid({ children, empty, className }: { children: React.ReactNode[]; empty: string; className?: string }) {
  if (children.length === 0) return <p className="text-muted-foreground text-sm">{empty}</p>;
  return <div className={cn("grid gap-4 sm:grid-cols-2 lg:grid-cols-3", className)}>{children}</div>;
}
