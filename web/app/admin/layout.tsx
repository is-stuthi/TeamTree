import { SectionNav } from "@/components/app/SectionNav";

const TABS = [
  { href: "/admin/skills", label: "Skill catalogue" },
  { href: "/admin/users", label: "Users & roles" },
];

// middleware.ts redirects non-admins; the API (require_admin) and MySQL procedures enforce it too.
export default function AdminLayout({ children }: { children: React.ReactNode }) {
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
