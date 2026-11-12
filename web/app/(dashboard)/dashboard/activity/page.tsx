import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { DASHBOARDS } from "@/specs/dashboards";

export const metadata = { title: "Activity · TeamTREE" };

export default async function ActivityPage() {
  return <SchemaDashboard spec={DASHBOARDS.my_activity} />;
}
