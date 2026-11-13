"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { EllipsisVertical, ExternalLink, LogOut, Settings2, Trash2, Undo2, type LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ConfirmDialog } from "./ConfirmDialog";
import { type ApiAction, useApiAction } from "./useApiAction";

// Icons by name: server pages can't pass component functions to this client component.
const ICONS = { open: ExternalLink, manage: Settings2, leave: LogOut, withdraw: Undo2, delete: Trash2 } satisfies Record<string, LucideIcon>;

interface Base { label: string; icon?: keyof typeof ICONS }
/** A menu item is either a link or an API call. Destructive calls are red, listed last, and always confirm. */
export type RowAction =
  | (Base & { href: string })
  | (Base & ApiAction & { destructive?: boolean; confirm?: string });

type Call = Extract<RowAction, ApiAction>;
const isCall = (a: RowAction): a is Call => !("href" in a);

export function RowActions({ actions, label = "More actions" }: { actions: RowAction[]; label?: string }) {
  const router = useRouter();
  const { pending, run } = useApiAction();
  const [open, setOpen] = useState(false);
  const [asking, setAsking] = useState<Call | null>(null);   // kept while the dialog animates out
  if (actions.length === 0) return null;

  const safe = actions.filter((a) => !isCall(a) || !a.destructive);
  const danger = actions.filter((a): a is Call => isCall(a) && !!a.destructive);
  const choose = (a: RowAction) => {
    if (!isCall(a)) return router.push(a.href);
    if (a.confirm || a.destructive) { setAsking(a); setOpen(true); } else run(a);
  };
  const item = (a: RowAction) => {
    const Icon = a.icon && ICONS[a.icon];
    return (
      <DropdownMenuItem key={a.label} variant={isCall(a) && a.destructive ? "destructive" : "default"} onClick={() => choose(a)}>
        {Icon && <Icon aria-hidden />}
        {a.label}
      </DropdownMenuItem>
    );
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" aria-label={label} disabled={pending} />}>
          <EllipsisVertical className="size-4" aria-hidden />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-44">
          {safe.map(item)}
          {safe.length > 0 && danger.length > 0 && <DropdownMenuSeparator />}
          {danger.map(item)}
        </DropdownMenuContent>
      </DropdownMenu>
      <ConfirmDialog open={open} onOpenChange={setOpen}
                     description={asking?.confirm ?? `${asking?.label}?`} confirmLabel={asking?.label ?? ""}
                     destructive={asking?.destructive} onConfirm={() => asking && run(asking)} />
    </>
  );
}
