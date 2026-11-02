"use client";

// Ranked horizontal bars (dataviz: compare parts / magnitude). Bars <= 24px thick
// with a 4px rounded data-end and square baseline; 2px gap between paired bars;
// a legend whenever there are two series; per-bar hover tooltip; value at the tip
// only for a single series (selective labels). The table view lives beside it.
import { Bar, BarChart, CartesianGrid, LabelList, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { rowsOf, type BarsWidget as Spec } from "../dashboard";
import { AXIS_TICK, GRID_STROKE, LEGEND_STYLE, SERIES, TOOLTIP_LABEL, TOOLTIP_STYLE } from "./chartTheme";

export function BarsWidget({ spec, data }: { spec: Spec; data: unknown }) {
  const rows = rowsOf(data, spec.path).slice(0, spec.limit ?? 12);
  if (rows.length === 0) return <p className="text-sm" style={{ color: "var(--viz-muted)" }}>Nothing to show.</p>;
  const series = spec.series.slice(0, 2);
  const barSize = series.length > 1 ? 10 : 14;
  const height = rows.length * (series.length * (barSize + 2) + 14) + 48;

  return (
    <div style={{ height }} role="img"
         aria-label={`${spec.title}: ${rows.map((r) => `${r[spec.label]} ${series.map((s) => `${s.label} ${r[s.key]}`).join(", ")}`).join("; ")}`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 32, bottom: 4, left: 4 }} barGap={2}>
          <CartesianGrid horizontal={false} stroke={GRID_STROKE} />
          <XAxis type="number" allowDecimals={false} tick={AXIS_TICK} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey={spec.label} width={130} tick={AXIS_TICK} axisLine={false} tickLine={false} />
          <Tooltip cursor={{ fill: "var(--viz-grid)", opacity: 0.4 }} contentStyle={TOOLTIP_STYLE} labelStyle={TOOLTIP_LABEL} />
          {series.length > 1 && <Legend wrapperStyle={LEGEND_STYLE} iconType="circle" iconSize={8} />}
          {series.map((s, i) => (
            <Bar key={s.key} dataKey={s.key} name={s.label} fill={SERIES[i]} barSize={barSize} radius={[0, 4, 4, 0]}>
              {series.length === 1 && <LabelList dataKey={s.key} position="right" style={{ fill: "var(--viz-ink-2)", fontSize: 12 }} />}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
