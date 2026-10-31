import { SectionNav } from "@/components/app/SectionNav";
import { getSession } from "@/lib/auth";

const TABS = [
  { href: "/dashboard", label: "Profile" },
  { href: "/dashboard/skills", label: "Skills" },
  { href: "/dashboard/projects", label: "Projects" },
  { href: "/dashboard/applications", label: "Applications" },
];

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession();
  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Hi, {session?.name.split(" ")[0]}</h1>
        <p className="text-muted-foreground text-sm">Your profile, skills, projects and teams.</p>
      </div>
      <SectionNav items={TABS} />
      {children}
    </main>
  );
}
