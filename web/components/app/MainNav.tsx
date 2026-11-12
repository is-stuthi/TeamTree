"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export interface MainNavItem {
  href: string;
  label: string;
}

/** Top-level nav with a clear active state; scrolls sideways on phones. */
export function MainNav({ items }: { items: MainNavItem[] }) {
  const pathname = usePathname();
  const section = (href: string) => "/" + href.split("/")[1];
  return (
    <nav aria-label="Main" className="no-scrollbar flex min-w-0 items-center gap-1 overflow-x-auto whitespace-nowrap text-sm">
      {items.map((item) => {
        const active = pathname === item.href || pathname.startsWith(section(item.href) + "/") || pathname === section(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "rounded-md px-3 py-1.5 font-medium transition-colors",
              active ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
