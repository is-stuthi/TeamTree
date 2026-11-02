import type { components } from "@/lib/api/schema";
import { ActionButton } from "./ActionButton";

type Endorsement = components["schemas"]["EndorsementSummary"];

/** Endorsements received, grouped by skill; the viewer can remove their own. */
export function EndorsementList({ endorsements, profileId, myId }: {
  endorsements: Endorsement[];
  profileId: number;
  myId: number;
}) {
  if (endorsements.length === 0) return <p className="text-muted-foreground text-sm">No endorsements yet.</p>;
  return (
    <ul className="space-y-3">
      {endorsements.map((e) => (
        <li key={e.skill_id} className="flex flex-wrap items-center justify-between gap-2 border-b pb-3 last:border-0">
          <div>
            <div className="font-medium">{e.skill}</div>
            <div className="text-muted-foreground text-xs">
              {e.count} endorsement{e.count > 1 ? "s" : ""} · average {e.avg_weight.toFixed(1)}/5 · by {e.endorsers.join(", ")}
            </div>
          </div>
          {e.endorser_ids.includes(myId) && (
            <ActionButton label="Remove mine" variant="ghost" method="DELETE" success="Endorsement removed"
                          path={`/graph/endorsements/${profileId}/${e.skill_id}`} />
          )}
        </li>
      ))}
    </ul>
  );
}
