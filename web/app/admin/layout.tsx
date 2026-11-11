import { redirect } from "next/navigation";
import { SectionTitle } from "@/components/app/SectionTitle";
import { getMe } from "@/lib/api/server";

// middleware.ts gates on the JWT (fast, may be stale); this layout re-checks the
// *live* role via the API. The API (require_admin) and MySQL procedures enforce it too.
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const me = await getMe();
  if (!me) redirect("/login?next=/admin/skills");
  if (me.role !== "admin") redirect("/dashboard");
  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <SectionTitle />
      {children}
    </div>
  );
}
