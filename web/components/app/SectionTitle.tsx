"use client";

import { usePathname } from "next/navigation";
import { PageHeader } from "./PageHeader";
import { activeNav } from "./nav";

/** Page title + description for the current route, taken from the nav config. */
export function SectionTitle({ descriptions = {} }: { descriptions?: Record<string, string> }) {
  const pathname = usePathname();
  const item = activeNav(pathname)?.item;
  if (!item || pathname !== item.href) return null;
  return <PageHeader title={item.label} description={descriptions[item.href] ?? item.description} />;
}
