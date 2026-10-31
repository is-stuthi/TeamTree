"use client";

import { useState } from "react";
import { buttonVariants } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { SchemaForm, type SchemaFormProps } from "@/components/schema/SchemaForm";

interface SpecDialogProps extends Omit<SchemaFormProps, "onSuccess"> {
  trigger: string;
  description?: string;
  variant?: "default" | "outline" | "secondary" | "ghost";
  size?: "default" | "sm";
}

/** Any schema-driven form in a dialog that closes itself on success. */
export function SpecDialog({ trigger, description, variant = "default", size = "default", ...form }: SpecDialogProps) {
  const [open, setOpen] = useState(false);
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger className={buttonVariants({ variant, size })}>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{form.spec.title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <SchemaForm {...form} onSuccess={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  );
}
