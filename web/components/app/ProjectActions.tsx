import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import type { UiSpec } from "@/components/schema/types";
import type { components } from "@/lib/api/schema";
import { ActionButton } from "./ActionButton";
import { SpecDialog } from "./SpecDialog";

type Detail = components["schemas"]["ProjectDetail"];

/** What the viewer can do on a project page: manage, apply, withdraw, or log in. */
export function ProjectActions({ project: p, loggedIn, applySpec }: { project: Detail; loggedIn: boolean; applySpec: UiSpec }) {
  const { viewer } = p;
  const full = p.max_team_size != null && p.team_size >= p.max_team_size;

  if (viewer.is_owner) {
    return <Link href={`/projects/${p.p_id}/manage/applications`} className={buttonVariants()}>Manage project</Link>;
  }
  if (viewer.is_member) return <Badge>You&apos;re on this team</Badge>;
  if (viewer.pending_application_id) {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="secondary">Application pending</Badge>
        <ActionButton label="Withdraw" method="POST" success="Application withdrawn" confirm="Withdraw your application?"
                      path={`/applications/${viewer.pending_application_id}/withdraw`} />
      </div>
    );
  }
  if (p.status !== "Open") return <Badge variant="outline">Not recruiting</Badge>;
  if (full) return <Badge variant="outline">Team is full</Badge>;
  if (!loggedIn) {
    return <Link href={`/login?next=/projects/${p.p_id}`} className={buttonVariants()}>Log in to apply</Link>;
  }
  return <SpecDialog spec={applySpec} trigger="Apply" params={{ p_id: p.p_id }}
                     description={`Your message goes to ${p.owner_name}, who reviews applications.`} />;
}
