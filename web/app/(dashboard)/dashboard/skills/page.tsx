import { MySkillList } from "@/components/app/MySkillList";
import { SpecDialog } from "@/components/app/SpecDialog";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "My skills · TeamTREE" };

export default async function SkillsPage() {
  const api = await serverApi();
  const [{ data: skills }, spec] = await Promise.all([api.GET("/users/me/skills"), getSpec("skill_add")]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>My skills</CardTitle>
        <CardDescription>Projects match you on these. Proficiency is per skill.</CardDescription>
        <CardAction>
          <SpecDialog spec={spec} trigger="+ Add skill" size="sm" resetOnSuccess
                      description="Choosing a skill you already have updates its level." />
        </CardAction>
      </CardHeader>
      <CardContent><MySkillList skills={skills ?? []} /></CardContent>
    </Card>
  );
}
