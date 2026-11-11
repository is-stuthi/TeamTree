import Link from "next/link";
import { NetworkIcon } from "lucide-react";

/** Brand mark: emerald tile + wordmark. */
export function Logo() {
  return (
    <Link href="/" className="flex shrink-0 items-center gap-2 rounded-md font-semibold tracking-tight" aria-label="TeamTREE home">
      <span className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-lg shadow-sm">
        <NetworkIcon className="size-4" aria-hidden />
      </span>
      <span className="hidden sm:inline">Team<span className="text-primary">TREE</span></span>
    </Link>
  );
}
