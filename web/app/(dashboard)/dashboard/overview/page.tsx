import { SchemaDashboard } from "@/components/schema/SchemaDashboard";
import { DASHBOARDS } from "@/specs/dashboards";

export const metadata = { title: "Overview · TeamTREE" };

export default async function OverviewPage() {
  return <SchemaDashboard spec={DASHBOARDS.my_dashboard} />;
}
