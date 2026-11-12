"use client";

import { usePathname } from "next/navigation";
import { PageHeader } from "./PageHeader";
import { activeNav } from "./nav";

/** Page title + description for the current route, from the nav config (per-route overrides; "" hides the description). */
export function SectionTitle({ titles = {}, descriptions = {} }: {
  titles?: Record<string, string>;
  descriptions?: Record<string, string>;
}) {
  const pathname = usePathname();
  const item = activeNav(pathname)?.item;
  if (!item || pathname !== item.href) return null;
  return <PageHeader title={titles[item.href] ?? item.label} description={descriptions[item.href] ?? item.description} />;
}
