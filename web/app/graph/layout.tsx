import { SectionNav } from "@/components/app/SectionNav";

const TABS = [
  { href: "/graph/network", label: "My network" },
  { href: "/graph/search", label: "Semantic search" },
];

export default function GraphLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Network</h1>
        <p className="text-muted-foreground text-sm">Powered by the Neo4j collaboration graph and vector search.</p>
      </div>
      <SectionNav items={TABS} />
      {children}
    </main>
  );
}
