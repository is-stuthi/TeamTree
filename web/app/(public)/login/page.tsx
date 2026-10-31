import Link from "next/link";
import { AuthCard } from "@/components/app/AuthCard";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec } from "@/lib/api/server";
import { safeNext } from "@/lib/route-guard";

export const metadata = { title: "Log in · TeamTREE" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const [{ next }, spec] = await Promise.all([searchParams, getSpec("login")]);
  return (
    <AuthCard
      title="Welcome back"
      description="Log in to manage your skills, projects and teams."
      footer={<span>New here? <Link href="/register" className="text-foreground underline">Create an account</Link></span>}
    >
      <SchemaForm spec={spec} action="/api/session" redirectTo={safeNext(next)} />
    </AuthCard>
  );
}
