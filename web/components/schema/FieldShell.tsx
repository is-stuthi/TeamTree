import { Label } from "@/components/ui/label";

interface FieldShellProps {
  id: string;
  label: string;
  required: boolean;
  help?: string | null;
  error?: string;
  children: React.ReactNode;
}

export function FieldShell({ id, label, required, help, error, children }: FieldShellProps) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>
        {label}
        {required && <span className="text-destructive" aria-hidden> *</span>}
      </Label>
      {children}
      {help && !error && <p className="text-muted-foreground text-xs">{help}</p>}
      {error && <p id={`${id}-error`} role="alert" className="text-destructive text-xs">{error}</p>}
    </div>
  );
}
