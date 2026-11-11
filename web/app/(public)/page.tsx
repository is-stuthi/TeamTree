import Link from "next/link";
import { ArrowRightIcon, CheckIcon, NetworkIcon, SparklesIcon, UsersIcon } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { cn } from "@/lib/utils";
import { DASHBOARDS } from "@/specs/dashboards";

const FEATURES = [
  { icon: SparklesIcon, title: "Skills, not résumés", body: "Add skills with proficiency levels and get matched to projects that need them." },
  { icon: UsersIcon, title: "Form real teams", body: "Owners define requirements, review applications and build their team." },
  { icon: NetworkIcon, title: "See the network", body: "Explore collaborators, endorsements and similar projects through a graph." },
];
const TRUST = ["Skill-matched recommendations", "Endorsements from teammates", "Free for students"];

export default async function Landing() {
  return (
    <div>
      <section className="relative isolate overflow-hidden border-b">
        <div className="hero-mesh absolute inset-0 -z-10" aria-hidden />
        <div className="dot-grid absolute inset-0 -z-10" aria-hidden />
        <div className="mx-auto max-w-4xl px-4 pt-20 pb-16 text-center sm:pt-28 sm:pb-24">
          <span className="bg-background/70 text-accent-foreground ring-primary/20 mb-8 inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium ring-1 backdrop-blur">
            <span className="bg-primary size-1.5 rounded-full" aria-hidden />
            Skill-based team formation
          </span>
          <h1 className="text-4xl leading-[1.1] font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
            Find teammates who have{" "}
            <span className="from-primary bg-gradient-to-r to-[var(--chart-2)] bg-clip-text text-transparent">the skills you need</span>
          </h1>
          <p className="text-muted-foreground mx-auto mt-6 max-w-2xl text-lg leading-relaxed sm:text-xl">
            Post a project, list the skills it needs, and TeamTREE shows you the people who can fill each role.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/register" className={cn(buttonVariants({ size: "lg" }), "h-12 w-full px-7 text-base shadow-lg shadow-primary/25 sm:w-auto")}>
              Get started <ArrowRightIcon className="size-4" aria-hidden />
            </Link>
            <Link href="/projects" className={cn(buttonVariants({ size: "lg", variant: "outline" }), "bg-background/70 h-12 w-full px-7 text-base sm:w-auto")}>
              Browse projects
            </Link>
          </div>
          <ul className="text-muted-foreground mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm">
            {TRUST.map((t) => (
              <li key={t} className="flex items-center gap-1.5">
                <CheckIcon className="text-primary size-4" aria-hidden />{t}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <div className="mx-auto max-w-6xl space-y-16 px-4 py-16">
        <section aria-labelledby="stats-h" className="space-y-4">
          <h2 id="stats-h" className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Live on TeamTREE</h2>
          <SchemaDashboard spec={DASHBOARDS.public_stats} />
        </section>
        <section aria-labelledby="how-h" className="space-y-8">
          <div className="space-y-2 text-center">
            <h2 id="how-h" className="text-3xl font-bold tracking-tight">How it works</h2>
            <p className="text-muted-foreground">From an idea to a working team in three steps.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="bg-card group rounded-2xl border p-6 transition-shadow hover:shadow-md">
                <span className="bg-accent text-accent-foreground mb-4 flex size-11 items-center justify-center rounded-xl">
                  <f.icon className="size-5" aria-hidden />
                </span>
                <h3 className="font-semibold">{f.title}</h3>
                <p className="text-muted-foreground mt-1.5 text-sm leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
