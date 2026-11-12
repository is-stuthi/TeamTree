import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-md space-y-4 px-4 py-24 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">Not found</h1>
      <p className="text-muted-foreground text-sm">That page, project or person doesn&apos;t exist.</p>
      <Link href="/projects" className={buttonVariants()}>Browse projects</Link>
    </div>
  );
}
