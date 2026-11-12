import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";
import { ActionButton } from "./ActionButton";
import { GraphUnavailable } from "./GraphUnavailable";

/** Admin editor for curated RELATED_TO edges in Neo4j (graph-only data: create/update/delete). */
export async function SkillRelations() {
  const api = await serverApi();
  const [{ data: rels, error }, spec] = await Promise.all([api.GET("/graph/skill-relations"), getSpec("relation_add")]);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Related skills (graph)</CardTitle>
        <CardDescription>Used for skill-gap suggestions. Saving an existing pair updates its strength.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        {error || !rels ? <GraphUnavailable what="Skill relations" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Skill</TableHead><TableHead>Related</TableHead><TableHead className="text-right">Strength</TableHead><TableHead /></TableRow></TableHeader>
            <TableBody>
              {rels.map((r) => (
                <TableRow key={`${r.a}-${r.b}`}>
                  <TableCell>{r.a_name}</TableCell><TableCell>{r.b_name}</TableCell>
                  <TableCell className="text-right tabular-nums">{r.weight.toFixed(1)}</TableCell>
                  <TableCell className="text-right">
                    <ActionButton label="Remove" variant="ghost" method="DELETE" path={`/graph/skills/${r.a}/related/${r.b}`}
                                  success={`Unlinked ${r.a_name} and ${r.b_name}`} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        <SchemaForm spec={spec} resetOnSuccess />
      </CardContent>
    </Card>
  );
}
