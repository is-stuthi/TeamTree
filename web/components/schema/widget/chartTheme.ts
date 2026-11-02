// Shared Recharts styling from the dataviz tokens (CSS variables on .viz-root),
// so light/dark swap in one place and marks follow the skill's specs.
import type { CSSProperties } from "react";

export const SERIES = ["var(--viz-series-1)", "var(--viz-series-2)"];
export const AXIS_TICK = { fill: "var(--viz-muted)", fontSize: 12 };
export const GRID_STROKE = "var(--viz-grid)";                 // hairline, solid, recessive

export const TOOLTIP_STYLE: CSSProperties = {
  background: "var(--viz-surface)",
  border: "1px solid var(--viz-grid)",
  borderRadius: 8,
  color: "var(--viz-ink)",
  fontSize: 12,
};
export const TOOLTIP_LABEL: CSSProperties = { color: "var(--viz-ink)", fontWeight: 600 };
export const LEGEND_STYLE: CSSProperties = { color: "var(--viz-ink-2)", fontSize: 12 };
