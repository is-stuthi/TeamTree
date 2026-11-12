// Registry of JSON dashboard specs. Adding a dashboard = a JSON file + one line here.
import type { DashboardSpec } from "@/components/schema/dashboard";
import applications from "./analytics_applications.json";
import projects from "./analytics_projects.json";
import skills from "./analytics_skills.json";
import teams from "./analytics_teams.json";
import users from "./analytics_users.json";
import myActivity from "./my_activity.json";
import myCharts from "./my_charts.json";
import myDashboard from "./my_dashboard.json";
import publicStats from "./public_stats.json";
import skillGap from "./skill_gap.json";

export const ANALYTICS_TABS: { key: string; label: string; spec: DashboardSpec; adminOnly: boolean }[] = [
  { key: "skills", label: "Skills", spec: skills as DashboardSpec, adminOnly: false },
  { key: "projects", label: "Projects", spec: projects as DashboardSpec, adminOnly: false },
  { key: "applications", label: "Applications", spec: applications as DashboardSpec, adminOnly: false },
  { key: "users", label: "Users", spec: users as DashboardSpec, adminOnly: true },
  { key: "teams", label: "Teams", spec: teams as DashboardSpec, adminOnly: true },
];

export const DASHBOARDS = {
  public_stats: publicStats as DashboardSpec,
  my_dashboard: myDashboard as DashboardSpec,
  my_activity: myActivity as DashboardSpec,
  my_charts: myCharts as DashboardSpec,
  skill_gap: skillGap as DashboardSpec,
};
