import Link from "next/link";
import { AuthCard } from "@/components/app/AuthCard";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec } from "@/lib/api/server";

export const metadata = { title: "Sign up · TeamTREE" };

export default async function RegisterPage() {
  const spec = await getSpec("register");
  return (
    <AuthCard
      title={spec.title}
      description="Add your skills next, then find or start a project."
      footer={<span>Already have an account? <Link href="/login" className="text-foreground underline">Log in</Link></span>}
    >
      <SchemaForm spec={spec} action="/api/session?mode=register" redirectTo="/dashboard/skills" />
    </AuthCard>
  );
}
