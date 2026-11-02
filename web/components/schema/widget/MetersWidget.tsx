import { CircleCheckIcon, OctagonAlertIcon } from "lucide-react";
import { rowsOf, type MetersWidget as Spec } from "../dashboard";

/** One meter per row: value against its own limit (dataviz "Meter": single ratio
 *  vs a limit, same-ramp track + fill). Text stays in ink tokens; the shortfall
 *  state carries an icon + label so it is never colour alone. */
export function MetersWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const rows = rowsOf(data, spec.path);
  if (rows.length === 0) return <p className="text-sm" style={{ color: "var(--viz-muted)" }}>Nothing to show.</p>;
  return (
    <ul className="space-y-3">
      {rows.map((r, i) => {
        const value = Number(r[spec.value]) || 0;
        const max = Math.max(Number(r[spec.max]) || 0, 1);
        const pct = Math.min(value / max, 1) * 100;
        const met = value >= max;
        return (
          <li key={i} className="space-y-1">
            <div className="flex items-baseline justify-between gap-2 text-sm">
              <span style={{ color: "var(--viz-ink)" }} className="font-medium">
                {String(r[spec.label])}
                {spec.sublabel && <span style={{ color: "var(--viz-ink-2)" }} className="font-normal"> · {String(r[spec.sublabel])}</span>}
              </span>
              <span className="flex items-center gap-1 tabular-nums" style={{ color: "var(--viz-ink-2)" }}>
                {met
                  ? <CircleCheckIcon className="size-3.5" style={{ color: "var(--viz-status-good)" }} aria-hidden />
                  : <OctagonAlertIcon className="size-3.5" style={{ color: "var(--viz-status-critical)" }} aria-hidden />}
                {value} of {max}{met ? "" : ` · need ${max - value}`}
              </span>
            </div>
            <div className="h-2 rounded-full" style={{ background: "var(--viz-track)" }}
                 role="meter" aria-valuemin={0} aria-valuemax={max} aria-valuenow={value}
                 aria-label={`${String(r[spec.label])}: ${value} of ${max}`}>
              <div className="h-2 rounded-full" style={{ width: `${pct}%`, background: "var(--viz-fill)" }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
