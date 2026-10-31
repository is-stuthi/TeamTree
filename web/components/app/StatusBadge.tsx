import { Badge } from "@/components/ui/badge";

type Variant = "default" | "secondary" | "outline" | "destructive";

const VARIANT: Record<string, Variant> = {
  // project lifecycle
  Open: "default", Ongoing: "secondary", Completed: "outline", Closed: "outline",
  // application
  Pending: "secondary", Accepted: "default", Rejected: "destructive", Withdrawn: "outline",
};

export function StatusBadge({ status }: { status: string }) {
  return <Badge variant={VARIANT[status] ?? "outline"}>{status}</Badge>;
}

export function OverdueBadge({ overdue }: { overdue: boolean }) {
  return overdue ? <Badge variant="destructive">Overdue</Badge> : null;
}
