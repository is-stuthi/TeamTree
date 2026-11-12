"use client";

import {
  AlertDialog, AlertDialogCancel, AlertDialogContent, AlertDialogDescription,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  description: string;
  confirmLabel: string;
  onConfirm: () => void;
  title?: string;
  destructive?: boolean;
}

/** "Are you sure?" popup for actions that change or remove data. Controlled, so it can open from a menu. */
export function ConfirmDialog({
  open, onOpenChange, description, confirmLabel, onConfirm, title = "Are you sure?", destructive = true,
}: ConfirmDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <Button variant={destructive ? "destructive" : "default"}
                  onClick={() => { onOpenChange(false); onConfirm(); }}>
            {confirmLabel}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
