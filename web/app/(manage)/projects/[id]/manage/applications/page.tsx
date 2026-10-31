import Link from "next/link";
import { ApplicationCard } from "@/components/app/ApplicationCard";
import { buttonVariants } from "@/components/ui/button";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Applications · TeamTREE" };

const STATUSES = ["Pending", "Accepted", "Rejected", "Withdrawn"] as const;
type Status = (typeof STATUSES)[number];

export default async function ApplicationsPage({ params, searchParams }: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ status?: Status }>;
}) {
  const p_id = Number((await params).id);
  const status = (await searchParams).status ?? "Pending";
  const api = await serverApi();
  const [{ data: apps = [] }, { data: all = [] }, acceptSpec] = await Promise.all([
    api.GET("/projects/{p_id}/applications", { params: { path: { p_id }, query: { status } } }),
    api.GET("/projects/{p_id}/applications", { params: { path: { p_id } } }),
    getSpec("application_accept"),
  ]);
  const count = (s: Status) => all.filter((a) => a.status === s).length;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Application status">
        {STATUSES.map((s) => (
          <Link key={s} href={`?status=${s}`} role="tab" aria-selected={s === status}
                className={buttonVariants({ variant: s === status ? "default" : "outline", size: "sm" })}>
            {s} ({count(s)})
          </Link>
        ))}
      </div>
      {apps.length === 0 ? (
        <p className="text-muted-foreground text-sm">No {status.toLowerCase()} applications.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {apps.map((a) => <ApplicationCard key={a.a_id} app={a} acceptSpec={acceptSpec} />)}
        </div>
      )}
    </div>
  );
}
