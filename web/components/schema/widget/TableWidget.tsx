import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { rowsOf, type TableWidget as Spec } from "../dashboard";

/** The table view: every chart has one, so no value is shown only as colour or length. */
export function TableWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const rows = rowsOf(data, spec.path);
  if (rows.length === 0) return <p className="text-muted-foreground text-sm">No rows.</p>;
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {spec.columns.map((c) => <TableHead key={c.key} className={c.align === "right" ? "text-right" : ""}>{c.label}</TableHead>)}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r, i) => (
          <TableRow key={i}>
            {spec.columns.map((c) => (
              <TableCell key={c.key} className={c.align === "right" ? "text-right tabular-nums" : ""}>
                {r[c.key] == null ? "—" : String(r[c.key])}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
