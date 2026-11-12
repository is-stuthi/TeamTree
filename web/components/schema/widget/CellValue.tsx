import { CalendarDays } from "lucide-react";
import { Pill, StatusBadge } from "@/components/app/StatusBadge";
import type { TableColumn } from "../dashboard";

const DAY = 86_400_000;
const startOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();

/** "Today", "Yesterday", "3 days ago", else "Oct 2" (or "Oct 2, 2025" in another year). */
export function dayLabel(d: Date, now = new Date()): string {
  const days = Math.round((startOfDay(now) - startOfDay(d)) / DAY);
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days > 1 && days < 7) return `${days} days ago`;
  return d.toLocaleDateString("en-US", {
    month: "short", day: "numeric", ...(d.getFullYear() !== now.getFullYear() && { year: "numeric" }),
  });
}

function DateCell({ value }: { value: string }) {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return <>{value}</>;
  const hasTime = d.getHours() + d.getMinutes() + d.getSeconds() > 0;   // date-only rows come back as 00:00:00
  const full = d.toLocaleString("en-US", { dateStyle: "full", ...(hasTime && { timeStyle: "short" }) });
  return (
    <time dateTime={value} title={full} className="inline-flex items-center gap-2 whitespace-nowrap">
      <span className="bg-muted text-foreground ring-border inline-flex h-6 items-center gap-1.5 rounded-md px-2 text-xs font-medium ring-1 ring-inset">
        <CalendarDays className="text-muted-foreground size-3.5" aria-hidden />
        {dayLabel(d)}
      </span>
      {hasTime && (
        <span className="text-muted-foreground text-xs tabular-nums">
          {d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
        </span>
      )}
    </time>
  );
}

/** One table cell, formatted per the column spec. */
export function CellValue({ column, value }: { column: TableColumn; value: unknown }) {
  if (value == null || value === "") return <span className="text-muted-foreground">—</span>;
  const text = String(value);
  if (column.format === "date") return <DateCell value={text} />;
  if (column.format === "badge") {
    const tone = column.tones?.[text];
    const label = text.charAt(0).toUpperCase() + text.slice(1);
    return tone ? <Pill tone={tone}>{label}</Pill> : <StatusBadge status={label} />;
  }
  return <>{text}</>;
}
