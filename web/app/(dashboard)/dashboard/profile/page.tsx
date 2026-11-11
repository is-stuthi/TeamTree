import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SchemaForm } from "@/components/schema/SchemaForm";
import { getSpec, serverApi } from "@/lib/api/server";

export const metadata = { title: "Profile · TeamTREE" };

export default async function ProfilePage() {
  const api = await serverApi();
  const [{ data: me }, profileSpec, passwordSpec] = await Promise.all([
    api.GET("/users/me"), getSpec("profile_edit"), getSpec("password_change"),
  ]);
  if (!me) return null;

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>{profileSpec.title}</CardTitle>
          <CardDescription>{me.email} · member since {new Date(me.created_at).toLocaleDateString()}</CardDescription>
        </CardHeader>
        <CardContent><SchemaForm spec={profileSpec} defaultValues={me} /></CardContent>
      </Card>
      <Card className="self-start">
        <CardHeader><CardTitle>{passwordSpec.title}</CardTitle></CardHeader>
        <CardContent><SchemaForm spec={passwordSpec} resetOnSuccess /></CardContent>
      </Card>
    </div>
  );
}
