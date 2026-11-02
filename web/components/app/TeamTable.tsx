import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { components } from "@/lib/api/schema";
import { ActionButton } from "./ActionButton";

type Member = components["schemas"]["TeamMember"];

/** Active and past members (history is kept). Owner view gets Remove buttons. */
export function TeamTable({ members, manageFor }: { members: Member[]; manageFor?: number }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Member</TableHead><TableHead>Role</TableHead><TableHead>Joined</TableHead>
          <TableHead>Left</TableHead><TableHead className="text-right">Open tasks</TableHead>{manageFor && <TableHead />}
        </TableRow>
      </TableHeader>
      <TableBody>
        {members.map((m) => (
          <TableRow key={m.j_id} className={m.is_active ? "" : "opacity-60"}>
            <TableCell className="font-medium">{m.member_name}</TableCell>
            <TableCell><Badge variant={m.role === "Owner" ? "default" : "secondary"}>{m.role}</Badge></TableCell>
            <TableCell>{m.join_date}</TableCell>
            <TableCell>{m.leave_date ?? "—"}</TableCell>
            <TableCell className="text-right tabular-nums">{m.is_active ? m.open_tasks : "—"}</TableCell>
            {manageFor && (
              <TableCell className="text-right">
                {m.is_active && m.role !== "Owner" && (
                  <ActionButton label="Remove" variant="destructive" method="DELETE"
                                path={`/projects/${manageFor}/team/${m.u_id}`} success={`${m.member_name} removed`}
                                confirm={`Remove ${m.member_name}? Their ${m.open_tasks} unfinished task(s) become unassigned. History is kept.`} />
                )}
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
