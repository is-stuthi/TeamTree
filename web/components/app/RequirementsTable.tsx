import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { components } from "@/lib/api/schema";
import { ActionButton } from "./ActionButton";

type Requirement = components["schemas"]["RequirementOut"];

interface RequirementsTableProps {
  requirements: Requirement[];
  editableFor?: number;           // project id: shows remove buttons (owner view)
}

export function RequirementsTable({ requirements, editableFor }: RequirementsTableProps) {
  if (requirements.length === 0) {
    return <p className="text-muted-foreground text-sm">No skill requirements yet.</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Skill</TableHead><TableHead>Role</TableHead><TableHead>Min. level</TableHead>
          <TableHead className="text-right">People</TableHead>{editableFor && <TableHead />}
        </TableRow>
      </TableHeader>
      <TableBody>
        {requirements.map((r) => (
          <TableRow key={`${r.s_id}-${r.req_role}`}>
            <TableCell className="font-medium">{r.s_name}</TableCell>
            <TableCell>{r.req_role}</TableCell>
            <TableCell><Badge variant="secondary">{r.p_s_level}</Badge></TableCell>
            <TableCell className="text-right tabular-nums">{r.req_count}</TableCell>
            {editableFor && (
              <TableCell className="text-right">
                <ActionButton label="Remove" method="DELETE" variant="ghost" success={`Removed ${r.s_name}`}
                              path={`/projects/${editableFor}/requirements/${r.s_id}?role=${encodeURIComponent(r.req_role)}`} />
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
