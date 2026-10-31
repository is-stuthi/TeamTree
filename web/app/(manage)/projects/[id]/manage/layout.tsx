import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { SectionNav } from "@/components/app/SectionNav";
import { StatusBadge } from "@/components/app/StatusBadge";
import { serverApi } from "@/lib/api/server";

// Owner-only area. middleware.ts requires login; this layout requires ownership,
// and every owner action is re-checked by the API / stored procedures.
export default async function ManageLayout({ children, params }: { children: React.ReactNode; params: Promise<{ id: string }> }) {
  const { id } = await params;
  const api = await serverApi();
  const { data: p } = await api.GET("/projects/{p_id}", { params: { path: { p_id: Number(id) } } });
  if (!p) notFound();
  if (!p.viewer.is_owner) redirect(`/projects/${id}`);

  const base = `/projects/${id}/manage`;
  const tabs = [
    { href: `${base}/applications`, label: "Applications" },
    { href: `${base}/requirements`, label: "Requirements" },
    { href: base, label: "Settings" },
  ];

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div className="space-y-1">
        <Link href={`/projects/${id}`} className="text-muted-foreground text-sm hover:underline">← Project page</Link>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">{p.p_name}</h1>
          <StatusBadge status={p.status} />
        </div>
      </div>
      <SectionNav items={tabs} />
      {children}
    </main>
  );
}
