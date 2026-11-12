"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "./ConfirmDialog";
import { type ApiAction, useApiAction } from "./useApiAction";

interface ActionButtonProps extends ApiAction {
  label: string;
  confirm?: string;             // shown in an "Are you sure?" dialog before running
  variant?: "default" | "outline" | "destructive" | "ghost" | "secondary";
}

/** One-click API action (reject, withdraw, remove...) followed by a refresh. */
export function ActionButton({ label, confirm, variant = "outline", ...action }: ActionButtonProps) {
  const { pending, run } = useApiAction();
  const [asking, setAsking] = useState(false);

  return (
    <>
      <Button size="sm" variant={variant} disabled={pending}
              onClick={() => (confirm ? setAsking(true) : run(action))}>
        {pending ? "…" : label}
      </Button>
      {confirm && (
        <ConfirmDialog open={asking} onOpenChange={setAsking} description={confirm}
                       confirmLabel={label} onConfirm={() => run(action)} />
      )}
    </>
  );
}
