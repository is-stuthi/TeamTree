import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { DASHBOARDS } from "@/specs/dashboards";

const FEATURES = [
  { title: "Skills, not résumés", body: "Add skills with proficiency levels and get matched to projects that need them." },
  { title: "Form real teams", body: "Owners define requirements, review applications and build their team." },
  { title: "See the network", body: "Explore collaborators, endorsements and similar projects through a graph." },
];

export default async function Landing() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-16 space-y-12">
      <section className="space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">TeamTREE</h1>
        <p className="text-muted-foreground text-lg">Find collaborators by skill. Build the team your project needs.</p>
        <div className="flex justify-center gap-3">
          <Link href="/register" className={buttonVariants({ size: "lg" })}>Get started</Link>
          <Link href="/projects" className={buttonVariants({ size: "lg", variant: "outline" })}>Browse projects</Link>
        </div>
      </section>
      <SchemaDashboard spec={DASHBOARDS.public_stats} />
      <section className="grid gap-4 sm:grid-cols-3">
        {FEATURES.map((f) => (
          <Card key={f.title}>
            <CardHeader>
              <CardTitle>{f.title}</CardTitle>
              <CardDescription>{f.body}</CardDescription>
            </CardHeader>
            <CardContent />
          </Card>
        ))}
      </section>
    </main>
  );
}
