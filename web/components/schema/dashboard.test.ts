import { describe, expect, it } from "vitest";
import spec from "@/specs/dashboards/skill_gap.json";
import { aggregate, fillPath, formatValue, pick, rowsOf, type DashboardSpec, type StatWidget } from "./dashboard";

const gap = [
  { s_name: "Docker", shortfall: 1, req_count: 1, qualified_members: 0 },
  { s_name: "Python", shortfall: 0, req_count: 1, qualified_members: 1 },
  { s_name: "React", shortfall: 0, req_count: 2, qualified_members: 2 },
];
const stat = (w: Partial<StatWidget>): StatWidget => ({ type: "stat", title: "t", source: "/x", ...w });

describe("dashboard helpers", () => {
  it("fills source placeholders", () => {
    expect(fillPath("/projects/{id}/skill-gap", { id: 3 })).toBe("/projects/3/skill-gap");
  });

  it("aggregates rows for stat tiles", () => {
    expect(aggregate(stat({ agg: "sum", field: "shortfall" }), gap)).toBe(1);
    expect(aggregate(stat({ agg: "count" }), gap)).toBe(3);
    expect(aggregate(stat({ agg: "count_where", field: "shortfall", equals: 0 }), gap)).toBe(2);
  });

  it("reads values from object responses by dot-path", () => {
    const data = { by_status: { Open: 6 }, acceptance_rate: 0.5 };
    expect(pick(data, "by_status.Open")).toBe(6);
    expect(aggregate(stat({ path: "acceptance_rate" }), data)).toBe(0.5);
    expect(rowsOf(data, "missing")).toEqual([]);
  });

  it("formats numbers and percents", () => {
    expect(formatValue(0.5, "percent")).toBe("50%");
    expect(formatValue(2.25)).toBe("2.3");
    expect(formatValue(null)).toBe("—");
  });

  it("the shipped skill-gap spec is well formed", () => {
    const s = spec as DashboardSpec;
    expect(s.widgets.map((w) => w.type)).toEqual(["stat", "stat", "stat", "meters", "table"]);
    expect(s.widgets.every((w) => w.source.startsWith("/projects/{id}/"))).toBe(true);
  });
});

describe("shipped dashboard specs", () => {
  it("every widget has a known type and an API source", async () => {
    const { ANALYTICS_TABS, DASHBOARDS } = await import("@/specs/dashboards");
    const specs = [...ANALYTICS_TABS.map((t) => t.spec), ...Object.values(DASHBOARDS)];
    for (const s of specs) {
      for (const w of s.widgets) {
        expect(["stat", "meters", "table", "bars", "line"]).toContain(w.type);
        expect(w.source.startsWith("/")).toBe(true);
        if (w.type === "bars") expect(w.series.length).toBeLessThanOrEqual(2);   // categorical cap: 2 validated slots
      }
    }
    expect(ANALYTICS_TABS.filter((t) => t.adminOnly).map((t) => t.key)).toEqual(["users", "teams"]);
  });
});
