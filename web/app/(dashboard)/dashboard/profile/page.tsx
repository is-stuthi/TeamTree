import { TriangleAlert } from "lucide-react";
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
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>{profileSpec.title}</CardTitle>
          <CardDescription>{me.email} · member since {new Date(me.created_at).toLocaleDateString()}</CardDescription>
        </CardHeader>
        <CardContent><SchemaForm spec={profileSpec} defaultValues={me} /></CardContent>
      </Card>

      <section aria-labelledby="danger-zone" className="space-y-3">
        <h2 id="danger-zone" className="text-destructive flex items-center gap-2 text-lg font-semibold">
          <TriangleAlert className="size-5" aria-hidden /> Danger zone
        </h2>
        <Card className="border-destructive/50 bg-destructive/5 ring-destructive/30">
          <CardHeader>
            <CardTitle className="text-destructive">{passwordSpec.title}</CardTitle>
            <CardDescription>You&apos;ll need your current password. Use the new one next time you log in.</CardDescription>
          </CardHeader>
          <CardContent className="max-w-md"><SchemaForm spec={passwordSpec} resetOnSuccess submitVariant="destructive" /></CardContent>
        </Card>
      </section>
    </div>
  );
}
