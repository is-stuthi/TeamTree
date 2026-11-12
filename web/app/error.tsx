"use client";

import Link from "next/link";
import { Button, buttonVariants } from "@/components/ui/button";

// Route-level error boundary: an unexpected failure shows a recoverable page
// instead of a blank screen. (Expected API errors are shown as toasts.)
export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="mx-auto max-w-md space-y-4 px-4 py-24 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">Something went wrong</h1>
      <p className="text-muted-foreground text-sm">
        The page couldn&apos;t be loaded. If the databases were restarted, give them a moment and try again.
      </p>
      {error.digest && <p className="text-muted-foreground font-mono text-xs">ref {error.digest}</p>}
      <div className="flex justify-center gap-2">
        <Button onClick={reset}>Try again</Button>
        <Link href="/" className={buttonVariants({ variant: "outline" })}>Home</Link>
      </div>
    </div>
  );
}
