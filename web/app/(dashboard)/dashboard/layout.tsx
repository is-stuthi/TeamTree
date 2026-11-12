import { redirect } from "next/navigation";
import { SectionTitle } from "@/components/app/SectionTitle";
import { getMe } from "@/lib/api/server";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const me = await getMe();                       // live: deactivated users are sent to login
  if (!me) redirect("/login?next=/dashboard");
  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <SectionTitle titles={{ "/dashboard": `Welcome back, ${me.f_name}` }} descriptions={{ "/dashboard": "" }} />
      {children}
    </div>
  );
}
