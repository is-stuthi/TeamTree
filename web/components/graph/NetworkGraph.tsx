"use client";

// Collaboration network (Neo4j COLLABORATED_WITH), force-directed on canvas.
// Colour = hop distance (3 categorical slots, validated all-pairs light + dark).
// Relief rule (light slot 3 is < 3:1): every node carries a visible name label,
// there is a legend, and the page lists the same people as text.
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import type { components } from "@/lib/api/schema";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

type Network = components["schemas"]["Network"];
type Node = Network["nodes"][number] & { x?: number; y?: number };

const DEGREE_LABEL = ["You", "Collaborator", "Collaborator of a collaborator"];
const DEGREE_VAR = ["--viz-series-1", "--viz-series-2", "--viz-series-3"];

export function NetworkGraph({ network, height = 420 }: { network: Network; height?: number }) {
  const router = useRouter();
  const box = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(600);
  const [colors, setColors] = useState<string[]>(["#2a78d6", "#eb6834", "#1baf7a"]);
  const [ink, setInk] = useState("#0b0b0b");

  useEffect(() => {
    if (!box.current) return;
    const css = getComputedStyle(box.current);
    setColors(DEGREE_VAR.map((v) => css.getPropertyValue(v).trim() || "#888"));
    setInk(css.getPropertyValue("--viz-ink").trim() || "#0b0b0b");
    const ro = new ResizeObserver(([e]) => setWidth(e.contentRect.width));
    ro.observe(box.current);
    return () => ro.disconnect();
  }, []);

  // Stable object identity: rebuilding on every render would restart the force layout.
  const data = useMemo(() => ({
    nodes: network.nodes.map((n) => ({ ...n })),
    links: network.edges.map((e) => ({ source: e.source, target: e.target, shared: e.shared })),
  }), [network]);

  return (
    <div ref={box} className="viz-root space-y-2">
      <div className="flex flex-wrap gap-4 text-xs" style={{ color: "var(--viz-ink-2)" }} aria-label="Legend">
        {DEGREE_LABEL.map((label, i) => (
          <span key={label} className="flex items-center gap-1.5">
            <span className="inline-block size-2.5 rounded-full" style={{ background: `var(${DEGREE_VAR[i]})` }} />{label}
          </span>
        ))}
      </div>
      <div className="overflow-hidden rounded-lg border" style={{ background: "var(--viz-surface)" }}
           role="img" aria-label={`Collaboration network with ${network.nodes.length} people`}>
        <ForceGraph2D
          graphData={data}
          width={width}
          height={height}
          backgroundColor="rgba(0,0,0,0)"
          linkColor={() => "rgba(137,135,129,0.55)"}
          linkWidth={(l) => 1 + Math.min(Number((l as { shared?: number }).shared ?? 1), 3) * 0.5}
          nodeLabel={(n) => `${(n as Node).name} · ${DEGREE_LABEL[(n as Node).degree] ?? ""}`}
          onNodeClick={(n) => router.push(`/users/${(n as Node).id}`)}
          nodeCanvasObject={(raw, ctx, scale) => {
            const n = raw as Node;
            const r = n.degree === 0 ? 7 : 5;                       // >= 8px marker diameter
            ctx.beginPath();
            ctx.arc(n.x ?? 0, n.y ?? 0, r, 0, 2 * Math.PI);
            ctx.fillStyle = colors[n.degree] ?? colors[2];
            ctx.fill();
            ctx.lineWidth = 2 / scale;                               // surface ring between overlapping marks
            ctx.strokeStyle = "rgba(252,252,251,0.9)";
            ctx.stroke();
            ctx.font = `${12 / scale}px system-ui, sans-serif`;
            ctx.fillStyle = ink;                                     // labels wear text ink, not series colour
            ctx.textAlign = "center";
            ctx.fillText(n.name, n.x ?? 0, (n.y ?? 0) + r + 12 / scale);
          }}
          nodePointerAreaPaint={(raw, color, ctx) => {
            const n = raw as Node;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(n.x ?? 0, n.y ?? 0, 12, 0, 2 * Math.PI);          // hit target bigger than the mark
            ctx.fill();
          }}
        />
      </div>
    </div>
  );
}
