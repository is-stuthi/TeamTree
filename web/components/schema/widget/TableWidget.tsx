import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { rowsOf, type TableWidget as Spec } from "../dashboard";

/** The table view: every chart has one, so no value is shown only as colour or length. */
export function TableWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const rows = rowsOf(data, spec.path);
  if (rows.length === 0) return <p className="text-muted-foreground bg-muted/50 rounded-lg border border-dashed py-8 text-center text-sm">Nothing here yet.</p>;
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {spec.columns.map((c) => <TableHead key={c.key} className={cn("text-muted-foreground text-xs font-medium uppercase tracking-wider", c.align === "right" && "text-right")}>{c.label}</TableHead>)}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r, i) => (
          <TableRow key={i}>
            {spec.columns.map((c) => (
              <TableCell key={c.key} className={cn("tabular-nums", c.align === "right" && "text-right font-medium")}>
                {r[c.key] == null ? "—" : String(r[c.key])}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
