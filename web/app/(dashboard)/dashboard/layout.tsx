import { redirect } from "next/navigation";
import { SectionNav } from "@/components/app/SectionNav";
import { getMe } from "@/lib/api/server";

const TABS = [
  { href: "/dashboard/overview", label: "Overview" },
  { href: "/dashboard", label: "Profile" },
  { href: "/dashboard/skills", label: "Skills" },
  { href: "/dashboard/projects", label: "Projects" },
  { href: "/dashboard/applications", label: "Applications" },
  { href: "/dashboard/teams", label: "Teams" },
  { href: "/dashboard/tasks", label: "Tasks" },
];

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const me = await getMe();                       // live: deactivated users are sent to login
  if (!me) redirect("/login?next=/dashboard");
  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Hi, {me.f_name}</h1>
        <p className="text-muted-foreground text-sm">Your profile, skills, projects and teams.</p>
      </div>
      <SectionNav items={TABS} />
      {children}
    </main>
  );
}
