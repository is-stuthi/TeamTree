import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { SectionNav } from "@/components/app/SectionNav";
import { StatusBadge } from "@/components/app/StatusBadge";
import { getProject } from "@/lib/api/server";

// Owner-only area. middleware.ts requires login; this layout requires ownership,
// and every owner action is re-checked by the API / stored procedures.
export default async function ManageLayout({ children, params }: { children: React.ReactNode; params: Promise<{ id: string }> }) {
  const { id } = await params;
  const p = Number.isInteger(Number(id)) ? await getProject(Number(id)) : null;
  if (!p) notFound();
  if (!p.viewer.is_owner) redirect(`/projects/${id}`);

  const base = `/projects/${id}/manage`;
  const tabs = [
    { href: `${base}/applications`, label: "Applications" },
    { href: `${base}/candidates`, label: "Candidates" },
    { href: `${base}/gap`, label: "Skill gap" },
    { href: `${base}/team`, label: "Team" },
    { href: `${base}/tasks`, label: "Tasks" },
    { href: `${base}/requirements`, label: "Requirements" },
    { href: base, label: "Settings" },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div className="space-y-1">
        <Link href={`/projects/${id}`} className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm transition-colors">← Project page</Link>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{p.p_name}</h1>
          <StatusBadge status={p.status} />
        </div>
      </div>
      <SectionNav items={tabs} />
      {children}
    </div>
  );
}
