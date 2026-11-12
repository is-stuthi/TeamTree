// Static renderer for JSON dashboard specs (web/specs/dashboards/*.json).
// A new dashboard or widget arrangement is JSON, not JSX. Server component:
// each widget's source is fetched on the server with the session token.
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchSource } from "@/lib/api/server";
import { cn } from "@/lib/utils";
import { fillPath, type DashboardSpec, type Widget } from "./dashboard";
import { BarsWidget } from "./widget/BarsWidget";
import { LineWidget } from "./widget/LineWidget";
import { MetersWidget } from "./widget/MetersWidget";
import { StatWidget } from "./widget/StatWidget";
import { TableWidget } from "./widget/TableWidget";

const SPAN = { 1: "", 2: "md:col-span-2", 3: "md:col-span-3" } as const;
const COLS = { 1: "", 2: "md:grid-cols-2", 3: "md:grid-cols-3" } as const;

function WidgetBody({ spec, data }: { spec: Widget; data: unknown }) {
  if (data === null) return <p className="text-muted-foreground text-sm">Couldn&apos;t load this data.</p>;
  switch (spec.type) {
    case "stat": return <StatWidget spec={spec} data={data} />;
    case "meters": return <MetersWidget spec={spec} data={data} />;
    case "table": return <TableWidget spec={spec} data={data} />;
    case "bars": return <BarsWidget spec={spec} data={data} />;
    case "line": return <LineWidget spec={spec} data={data} />;
  }
}

export async function SchemaDashboard({ spec, params }: { spec: DashboardSpec; params?: Record<string, string | number> }) {
  // Widgets sharing a source share one request (fetchSource is cached per render).
  const data = await Promise.all(spec.widgets.map((w) => fetchSource(fillPath(w.source, params))));
  return (
    <div className={cn("viz-root grid gap-4", COLS[spec.grid?.cols ?? 3])}>
      {spec.widgets.map((w, i) => (
        <Card key={`${w.type}-${i}`} className={cn(SPAN[w.span ?? 1], "transition-shadow hover:shadow-md")}>
          <CardHeader>
            <CardTitle className={w.type === "stat" ? "text-muted-foreground text-sm font-medium" : "text-base font-semibold"}>{w.title}</CardTitle>
            {w.help && <CardDescription>{w.help}</CardDescription>}
          </CardHeader>
          <CardContent><WidgetBody spec={w} data={data[i]} /></CardContent>
        </Card>
      ))}
    </div>
  );
}
