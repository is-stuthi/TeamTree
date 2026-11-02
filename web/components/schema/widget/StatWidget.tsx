import { CircleCheckIcon, OctagonAlertIcon } from "lucide-react";
import { aggregate, formatValue, type StatWidget as Spec } from "../dashboard";

/** Stat tile: one headline number (dataviz: "a single current value" is not a chart). */
export function StatWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const value = aggregate(spec, data);
  const good = value === null || !spec.good_when ? null
    : spec.good_when === "zero" ? value === 0 : value > 0;
  return (
    <div className="space-y-1">
      <div className="text-4xl font-semibold" style={{ color: "var(--viz-ink)" }}>{formatValue(value, spec.format)}</div>
      {good !== null && (
        <div className="flex items-center gap-1.5 text-sm" style={{ color: "var(--viz-ink-2)" }}>
          {good
            ? <CircleCheckIcon className="size-4" style={{ color: "var(--viz-status-good)" }} aria-hidden />
            : <OctagonAlertIcon className="size-4" style={{ color: "var(--viz-status-critical)" }} aria-hidden />}
          {good ? "On track" : "Needs attention"}
        </div>
      )}
    </div>
  );
}
