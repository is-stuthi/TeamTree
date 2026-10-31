"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";
import { messageFor } from "@/lib/errors";

type AdminUser = components["schemas"]["AdminUserOut"];
type Role = AdminUser["role"];
const ROLES = [{ value: "member", label: "member" }, { value: "admin", label: "admin" }];

export function AdminUsersTable({ users, currentUserId }: { users: AdminUser[]; currentUserId: number }) {
  const router = useRouter();
  const [pending, start] = useTransition();

  const run = (label: string, call: () => Promise<{ error?: unknown }>) => start(async () => {
    const { error } = await call();
    if (error) toast.error(messageFor(error as { code?: string }));
    else toast.success(label);
    router.refresh();
  });

  const setRole = (u: AdminUser, role: Role) => run(`${u.name} is now ${role}`, () =>
    api.PUT("/admin/users/{user_id}/role", { params: { path: { user_id: u.id } }, body: { role } }));

  const deactivate = (u: AdminUser) => run(`${u.name} deactivated`, () =>
    api.POST("/admin/users/{user_id}/deactivate", { params: { path: { user_id: u.id } } }));

  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Name</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Status</TableHead><TableHead /></TableRow>
      </TableHeader>
      <TableBody>
        {users.map((u) => {
          const locked = pending || !u.is_active || u.id === currentUserId;
          return (
            <TableRow key={u.id} className={u.is_active ? "" : "opacity-60"}>
              <TableCell className="font-medium">{u.name}{u.id === currentUserId && " (you)"}</TableCell>
              <TableCell className="text-muted-foreground">{u.email}</TableCell>
              <TableCell className="w-36">
                <Select items={ROLES} value={u.role} disabled={locked} onValueChange={(v) => v && v !== u.role && setRole(u, v as Role)}>
                  <SelectTrigger size="sm" className="w-full" aria-label={`Role for ${u.name}`}><SelectValue /></SelectTrigger>
                  <SelectContent>{ROLES.map((r) => <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>)}</SelectContent>
                </Select>
              </TableCell>
              <TableCell><Badge variant={u.is_active ? "secondary" : "outline"}>{u.is_active ? "active" : "deactivated"}</Badge></TableCell>
              <TableCell className="text-right">
                <Button variant="destructive" size="sm" disabled={locked} onClick={() => deactivate(u)}>Deactivate</Button>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
