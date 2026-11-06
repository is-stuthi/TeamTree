import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { components } from "@/lib/api/schema";
import { InlineSelect, type InlineOption } from "./InlineSelect";

type Task = components["schemas"]["TaskOut"] & { depth?: number; p_name?: string };

const STATUSES: InlineOption[] = ["To Do", "In Progress", "Done", "Blocked"].map((s) => ({ value: s, label: s }));
const PRIORITY = { Low: "outline", Medium: "secondary", High: "default", Critical: "destructive" } as const;

interface TaskTableProps {
  tasks: Task[];
  members?: InlineOption[];       // active team members -> assignee select (owner/member view)
  showProject?: boolean;          // "my tasks" across projects
}

/** Tasks as a table; when rows carry `depth` (Q8 tree) names are indented. */
export function TaskTable({ tasks, members, showProject }: TaskTableProps) {
  if (tasks.length === 0) return <p className="text-muted-foreground text-sm">No tasks yet.</p>;
  const assignees: InlineOption[] = [{ value: "none", label: "Unassigned" }, ...(members ?? [])];
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Task</TableHead>{showProject && <TableHead>Project</TableHead>}
          <TableHead>Status</TableHead><TableHead>Priority</TableHead>
          <TableHead>Assignee</TableHead><TableHead>Due</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {tasks.map((t) => (
          <TableRow key={t.task_id}>
            <TableCell className="font-medium">
              <span style={{ paddingLeft: `${(t.depth ?? 0) * 1.25}rem` }}>
                {(t.depth ?? 0) > 0 && <span className="text-muted-foreground">↳ </span>}{t.t_name}
              </span>
            </TableCell>
            {showProject && <TableCell className="text-muted-foreground">{t.p_name}</TableCell>}
            <TableCell className="w-40">
              <InlineSelect value={t.status} options={STATUSES} method="PATCH" path={`/tasks/${t.task_id}`}
                            field="status" label={`Status of ${t.t_name}`}
                            success={`“${t.t_name}” → {label}`} />
            </TableCell>
            <TableCell><Badge variant={PRIORITY[t.priority]}>{t.priority}</Badge></TableCell>
            <TableCell className="w-44">
              {members ? (
                <InlineSelect value={t.u_id ? String(t.u_id) : "none"} options={assignees} method="POST"
                              path={`/tasks/${t.task_id}/assign`} label={`Assignee of ${t.t_name}`}
                              field="u_id" kind="id" success="Assigned to {label}" />
              ) : (
                <span className="text-muted-foreground">{t.assignee_name ?? "Unassigned"}</span>
              )}
            </TableCell>
            <TableCell className={t.is_overdue ? "text-destructive font-medium" : "text-muted-foreground"}>
              {t.due_date ?? "—"}{t.is_overdue && " (overdue)"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
