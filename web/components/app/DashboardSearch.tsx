import { Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Big search bar for the dashboard. A plain GET form (no JS): "Search" goes to the
 * keyword project browser, "By meaning" to Neo4j vector search. Navigation, not a
 * data form, so it is not a SchemaForm spec.
 */
export function DashboardSearch() {
  return (
    <form action="/projects" method="get" role="search"
          className="bg-card focus-within:ring-ring/40 flex flex-col gap-2 rounded-2xl border p-2 shadow-sm transition focus-within:ring-4 sm:flex-row sm:items-center">
      <label className="flex min-w-0 flex-1 items-center gap-3 px-3">
        <Search className="text-muted-foreground size-6 shrink-0" aria-hidden />
        <span className="sr-only">Search projects</span>
        <input name="q" type="search" required minLength={2} autoComplete="off"
               placeholder="Search projects, skills or ideas…"
               className="placeholder:text-muted-foreground h-14 w-full min-w-0 bg-transparent text-lg outline-none sm:text-xl" />
      </label>
      <div className="flex gap-2">
        {/* Search comes first in the DOM so Enter runs the keyword search; `order` keeps it on the right. */}
        <Button type="submit" size="lg" className="order-2 h-12 flex-1 px-6 sm:flex-none">Search</Button>
        <Button type="submit" variant="outline" size="lg" formAction="/graph/search" className="order-1 h-12 flex-1 sm:flex-none">
          <Sparkles aria-hidden /> By meaning
        </Button>
      </div>
    </form>
  );
}
