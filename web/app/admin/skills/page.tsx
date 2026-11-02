import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { SkillRelations } from "@/components/app/SkillRelations";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Skill catalogue · TeamTREE" };

export default async function AdminSkillsPage() {
  const api = await serverApi();
  const [{ data: skills = [] }, spec] = await Promise.all([api.GET("/skills"), getSpec("skill_admin")]);

  return (
    <div className="space-y-6">
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Catalogue</CardTitle>
          <CardDescription>{skills.length} skills. Names are unique ignoring case and spaces.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow><TableHead>Skill</TableHead><TableHead>Category</TableHead><TableHead className="text-right">Users</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {skills.map((s) => (
                <TableRow key={s.s_id}>
                  <TableCell className="font-medium">{s.s_name}</TableCell>
                  <TableCell>{s.category && <Badge variant="outline">{s.category}</Badge>}</TableCell>
                  <TableCell className="text-right tabular-nums">{s.users_possessing}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      <Card className="self-start">
        <CardHeader><CardTitle>{spec.title}</CardTitle></CardHeader>
        <CardContent><SchemaForm spec={spec} resetOnSuccess /></CardContent>
      </Card>
    </div>
    <SkillRelations />
    </div>
  );
}
