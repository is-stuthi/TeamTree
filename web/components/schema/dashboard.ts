// Dashboard spec contract + pure helpers (unit-tested). Widgets never compute
// metrics beyond these simple aggregations: SQL views/queries do the real work.

interface WidgetBase {
  title: string;
  source: string;              // GET path; {placeholders} filled from params
  path?: string;               // dot-path into an object response
  span?: 1 | 2 | 3;
  help?: string;
}

export interface StatWidget extends WidgetBase {
  type: "stat";
  agg?: "sum" | "count" | "count_where" | "value";
  field?: string;
  equals?: string | number;
  format?: "number" | "percent";
  good_when?: "zero" | "positive";   // adds a status icon + label, never colour alone
}

export interface MetersWidget extends WidgetBase {
  type: "meters";
  label: string;
  sublabel?: string;
  value: string;
  max: string;
}

export interface TableWidget extends WidgetBase {
  type: "table";
  columns: { key: string; label: string; align?: "right" }[];
}

/** Horizontal ranked bars; 1 series (single hue) or 2 series (categorical slots 1-2 + legend). */
export interface BarsWidget extends WidgetBase {
  type: "bars";
  label: string;
  series: { key: string; label: string }[];
  limit?: number;
}

/** Single-series trend over time: 2px line on a ~10% wash, crosshair tooltip. */
export interface LineWidget extends WidgetBase {
  type: "line";
  x: string;
  y: string;
  y_label: string;
}

export type Widget = StatWidget | MetersWidget | TableWidget | BarsWidget | LineWidget;

export interface DashboardSpec {
  title: string;
  description?: string;
  grid?: { cols: 1 | 2 | 3 };
  widgets: Widget[];
}

export type Row = Record<string, unknown>;

export function fillPath(source: string, params: Record<string, string | number> = {}): string {
  return source.replace(/\{(\w+)\}/g, (_, k: string) => encodeURIComponent(String(params[k] ?? "")));
}

export function pick(data: unknown, path?: string): unknown {
  if (!path) return data;
  return path.split(".").reduce<unknown>((v, key) => (v && typeof v === "object" ? (v as Row)[key] : undefined), data);
}

export function rowsOf(data: unknown, path?: string): Row[] {
  const v = pick(data, path);
  return Array.isArray(v) ? (v as Row[]) : [];
}

export function aggregate(w: StatWidget, data: unknown): number | null {
  const agg = w.agg ?? "value";
  if (agg === "value") {
    const v = Number(pick(data, w.path));
    return Number.isFinite(v) ? v : null;
  }
  const rows = rowsOf(data, w.path);
  if (agg === "count") return rows.length;
  if (agg === "count_where") return rows.filter((r) => r[w.field ?? ""] === w.equals).length;
  return rows.reduce((sum, r) => sum + (Number(r[w.field ?? ""]) || 0), 0);
}

export function formatValue(v: number | null, format: StatWidget["format"] = "number"): string {
  if (v === null) return "—";
  if (format === "percent") return `${Math.round(v * 100)}%`;
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}
