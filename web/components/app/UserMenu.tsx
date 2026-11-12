"use client";

import { useRouter } from "next/navigation";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { AppRole } from "@/lib/session";

const initials = (name: string) => name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();

export function UserMenu({ name, role }: { name: string; role: AppRole }) {
  const router = useRouter();

  const logout = async () => {
    await fetch("/api/session", { method: "DELETE" });
    router.push("/");
    router.refresh();
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-2 rounded-full outline-none" aria-label="Account menu">
        <Avatar className="size-8"><AvatarFallback>{initials(name)}</AvatarFallback></Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuGroup>
          <DropdownMenuLabel className="flex items-center justify-between gap-2">
            <span className="truncate">{name}</span>
            <Badge variant={role === "admin" ? "default" : "secondary"}>{role}</Badge>
          </DropdownMenuLabel>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => router.push("/dashboard/profile")}>Profile</DropdownMenuItem>
        <DropdownMenuItem onClick={() => router.push("/dashboard/skills")}>My skills</DropdownMenuItem>
        {role === "admin" && <DropdownMenuItem onClick={() => router.push("/admin/skills")}>Admin</DropdownMenuItem>}
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout}>Log out</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
