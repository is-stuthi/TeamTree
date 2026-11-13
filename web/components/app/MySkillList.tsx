"use client";

import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { components } from "@/lib/api/schema";
import { RowActions } from "./RowActions";

type UserSkill = components["schemas"]["UserSkillOut"];

const LEVEL_VARIANT = { Beginner: "outline", Intermediate: "secondary", Advanced: "default", Expert: "default" } as const;

export function MySkillList({ skills }: { skills: UserSkill[] }) {
  if (skills.length === 0) {
    return <p className="text-muted-foreground text-sm">No skills yet. Add your first one to start getting matched.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Skill</TableHead><TableHead>Category</TableHead><TableHead>Level</TableHead><TableHead /></TableRow>
      </TableHeader>
      <TableBody>
        {skills.map((s) => (
          <TableRow key={s.s_id}>
            <TableCell className="font-medium">{s.s_name}</TableCell>
            <TableCell className="text-muted-foreground">{s.category}</TableCell>
            <TableCell><Badge variant={LEVEL_VARIANT[s.u_s_level]}>{s.u_s_level}</Badge></TableCell>
            <TableCell className="w-10 text-right">
              <RowActions label={`Actions for ${s.s_name}`} actions={[{
                label: "Remove skill", icon: "delete", destructive: true, method: "DELETE",
                path: `/users/me/skills/${s.s_id}`, success: `Removed ${s.s_name}`,
                confirm: `${s.s_name} will be removed from your profile, so projects will stop matching you on it. You can add it again later.`,
              }]} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
