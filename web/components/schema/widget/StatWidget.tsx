import { CircleCheckIcon, OctagonAlertIcon } from "lucide-react";
import { aggregate, formatValue, type StatWidget as Spec } from "../dashboard";

/** Stat tile: one headline number (dataviz: "a single current value" is not a chart). */
export function StatWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const value = aggregate(spec, data);
  const good = value === null || !spec.good_when ? null
    : spec.good_when === "zero" ? value === 0 : value > 0;
  return (
    <div className="space-y-2">
      <div className="tabular text-4xl font-bold tracking-tight" style={{ color: "var(--viz-ink)" }}>{formatValue(value, spec.format)}</div>
      {good !== null && (
        <div
          className="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium"
          style={{
            color: good ? "var(--viz-status-good)" : "var(--viz-status-critical)",
            background: `color-mix(in oklch, ${good ? "var(--viz-status-good)" : "var(--viz-status-critical)"} 12%, transparent)`,
          }}
        >
          {good ? <CircleCheckIcon className="size-3.5" aria-hidden /> : <OctagonAlertIcon className="size-3.5" aria-hidden />}
          {good ? "On track" : "Needs attention"}
        </div>
      )}
    </div>
  );
}
