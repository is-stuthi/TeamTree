import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { components } from "@/lib/api/schema";
import type { UiSpec } from "@/components/schema/types";
import { ActionButton } from "./ActionButton";
import { SpecDialog } from "./SpecDialog";
import { StatusBadge } from "./StatusBadge";

type Received = components["schemas"]["ReceivedApplication"];

/** One received application in the owner's review queue. */
export function ApplicationCard({ app, acceptSpec }: { app: Received; acceptSpec: UiSpec }) {
  const match = app.total_requirements ? `${app.matched_requirements}/${app.total_requirements} requirements met` : null;
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle><Link href={`/users/${app.applicant_id}`} className="hover:underline">{app.applicant_name}</Link></CardTitle>
          <StatusBadge status={app.status} />
        </div>
        <CardDescription>
          {app.experience_level} · {app.availability} · applied {new Date(app.a_date).toLocaleDateString()}
          {match && <> · <span className="text-foreground font-medium">{match}</span></>}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {app.msg && <p className="text-sm whitespace-pre-line">{app.msg}</p>}
        <div className="flex flex-wrap gap-1.5">
          {app.skills.map((s) => <Badge key={s.s_name} variant="outline">{s.s_name} · {s.level}</Badge>)}
        </div>
      </CardContent>
      {app.status === "Pending" && (
        <CardFooter className="gap-2">
          <SpecDialog spec={acceptSpec} trigger="Accept" size="sm" params={{ a_id: app.a_id }}
                      description={`${app.applicant_name} joins the team immediately (one transaction).`} />
          <ActionButton label="Reject" variant="destructive" method="POST" success="Application rejected"
                        path={`/applications/${app.a_id}/decision`} body={{ decision: "Rejected" }} />
        </CardFooter>
      )}
    </Card>
  );
}
