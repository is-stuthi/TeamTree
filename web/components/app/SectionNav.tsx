"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export interface NavItem {
  href: string;
  label: string;
}

/** Segmented tab navigation for a section (dashboard, admin, project manage). */
export function SectionNav({ items }: { items: NavItem[] }) {
  const pathname = usePathname();
  return (
    <nav className="no-scrollbar bg-muted/70 flex w-fit max-w-full gap-1 overflow-x-auto rounded-xl border p-1" aria-label="Section">
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "rounded-lg px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-all",
              active ? "bg-background text-foreground shadow-sm ring-1 ring-border" : "text-muted-foreground hover:text-foreground",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
