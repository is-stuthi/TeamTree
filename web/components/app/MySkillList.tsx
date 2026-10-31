"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { XIcon } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";
import { messageFor } from "@/lib/errors";

type UserSkill = components["schemas"]["UserSkillOut"];

const LEVEL_VARIANT = { Beginner: "outline", Intermediate: "secondary", Advanced: "default", Expert: "default" } as const;

export function MySkillList({ skills }: { skills: UserSkill[] }) {
  const router = useRouter();
  const [pending, start] = useTransition();

  const remove = (s: UserSkill) => start(async () => {
    const { error } = await api.DELETE("/users/me/skills/{s_id}", { params: { path: { s_id: s.s_id } } });
    if (error) toast.error(messageFor(error as { code?: string }));
    else toast.success(`Removed ${s.s_name}`);
    router.refresh();
  });

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
            <TableCell className="text-right">
              <Button variant="ghost" size="icon-sm" disabled={pending} onClick={() => remove(s)} aria-label={`Remove ${s.s_name}`}>
                <XIcon />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
