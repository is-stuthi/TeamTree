import { MySkillList } from "@/components/app/MySkillList";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "My skills · TeamTREE" };

export default async function SkillsPage() {
  const api = await serverApi();
  const [{ data: skills }, spec] = await Promise.all([api.GET("/users/me/skills"), getSpec("skill_add")]);

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>My skills</CardTitle>
          <CardDescription>Projects match you on these. Proficiency is per skill.</CardDescription>
        </CardHeader>
        <CardContent><MySkillList skills={skills ?? []} /></CardContent>
      </Card>
      <Card className="self-start">
        <CardHeader>
          <CardTitle>{spec.title}</CardTitle>
          <CardDescription>Choosing a skill you already have updates its level.</CardDescription>
        </CardHeader>
        <CardContent><SchemaForm spec={spec} resetOnSuccess /></CardContent>
      </Card>
    </div>
  );
}
