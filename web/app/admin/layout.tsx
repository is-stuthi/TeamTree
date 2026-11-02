import { redirect } from "next/navigation";
import { SectionNav } from "@/components/app/SectionNav";
import { getMe } from "@/lib/api/server";

const TABS = [
  { href: "/admin/skills", label: "Skill catalogue" },
  { href: "/admin/users", label: "Users & roles" },
];

// middleware.ts gates on the JWT (fast, may be stale); this layout re-checks the
// *live* role via the API. The API (require_admin) and MySQL procedures enforce it too.
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const me = await getMe();
  if (!me) redirect("/login?next=/admin/skills");
  if (me.role !== "admin") redirect("/dashboard");
  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Administration</h1>
        <p className="text-muted-foreground text-sm">Manage the skill catalogue and user roles.</p>
      </div>
      <SectionNav items={TABS} />
      {children}
    </main>
  );
}
