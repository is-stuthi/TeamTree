"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { activeNav } from "./nav";

/** "Group › Page" trail, derived from the nav config so it always matches the sidebar. */
export function AppBreadcrumb() {
  const pathname = usePathname();
  const match = activeNav(pathname);
  if (!match) return null;
  const { group, item } = match;
  const deeper = pathname !== item.href;

  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem className="hidden sm:inline-flex">{group.label}</BreadcrumbItem>
        <BreadcrumbSeparator className="hidden sm:inline-flex" />
        <BreadcrumbItem>
          {deeper
            ? <BreadcrumbLink render={<Link href={item.href} />}>{item.label}</BreadcrumbLink>
            : <BreadcrumbPage>{item.label}</BreadcrumbPage>}
        </BreadcrumbItem>
        {deeper && (
          <>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Details</BreadcrumbPage></BreadcrumbItem>
          </>
        )}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
