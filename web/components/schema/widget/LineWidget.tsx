"use client";

// Single-series trend (dataviz: area for one series over time). 2px line, ~10%
// wash, no legend (the title names the series), crosshair + tooltip on hover,
// >= 8px active dot with a surface ring.
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { rowsOf, type LineWidget as Spec } from "../dashboard";
import { AXIS_TICK, GRID_STROKE, SERIES, TOOLTIP_LABEL, TOOLTIP_STYLE } from "./chartTheme";

const shortDate = (v: unknown) => String(v).slice(5);          // 2026-11-02 -> 11-02

export function LineWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const rows = rowsOf(data, spec.path);
  if (rows.length === 0) return <p className="text-sm" style={{ color: "var(--viz-muted)" }}>Nothing to show.</p>;
  const total = rows.reduce((s, r) => s + (Number(r[spec.y]) || 0), 0);

  return (
    <div style={{ height: 220 }} role="img" aria-label={`${spec.title}: ${total} ${spec.y_label} over ${rows.length} days`}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID_STROKE} />
          <XAxis dataKey={spec.x} tickFormatter={shortDate} tick={AXIS_TICK} axisLine={{ stroke: GRID_STROKE }}
                 tickLine={false} interval="preserveStartEnd" minTickGap={24} />
          <YAxis allowDecimals={false} width={28} tick={AXIS_TICK} axisLine={false} tickLine={false} />
          <Tooltip cursor={{ stroke: "var(--viz-muted)", strokeWidth: 1 }} contentStyle={TOOLTIP_STYLE}
                   labelStyle={TOOLTIP_LABEL} formatter={(v) => [v, spec.y_label]} />
          <Area type="monotone" dataKey={spec.y} name={spec.y_label} stroke={SERIES[0]} strokeWidth={2}
                fill={SERIES[0]} fillOpacity={0.1} dot={false}
                activeDot={{ r: 4, stroke: "var(--viz-surface)", strokeWidth: 2, fill: SERIES[0] }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
