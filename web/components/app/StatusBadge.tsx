import { cn } from "@/lib/utils";

type Tone = "success" | "info" | "warning" | "danger" | "neutral";

const TONE: Record<string, Tone> = {
  // project lifecycle
  Open: "success", Ongoing: "info", Completed: "neutral", Closed: "neutral",
  // application
  Pending: "warning", Accepted: "success", Rejected: "danger", Withdrawn: "neutral",
};

// Dot + label so meaning never relies on colour alone (dashboard-design §5).
const STYLE: Record<Tone, { pill: string; dot: string }> = {
  success: { pill: "bg-success/12 text-success ring-success/25", dot: "bg-success" },
  info: { pill: "bg-info/12 text-info ring-info/25", dot: "bg-info" },
  warning: { pill: "bg-warning/15 text-[color-mix(in_oklch,var(--warning)_70%,var(--foreground))] ring-warning/30", dot: "bg-warning" },
  danger: { pill: "bg-destructive/12 text-destructive ring-destructive/25", dot: "bg-destructive" },
  neutral: { pill: "bg-muted text-muted-foreground ring-border", dot: "bg-muted-foreground/60" },
};

function Pill({ tone, children }: { tone: Tone; children: React.ReactNode }) {
  const s = STYLE[tone];
  return (
    <span className={cn("inline-flex h-6 shrink-0 items-center gap-1.5 rounded-full px-2.5 text-xs font-medium whitespace-nowrap ring-1 ring-inset", s.pill)}>
      <span className={cn("size-1.5 rounded-full", s.dot)} aria-hidden />
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  return <Pill tone={TONE[status] ?? "neutral"}>{status}</Pill>;
}

export function OverdueBadge({ overdue }: { overdue: boolean }) {
  return overdue ? <Pill tone="danger">Overdue</Pill> : null;
}
