import { redirect } from "next/navigation";

// Overview now lives at /dashboard; keep the old URL working.
export default function OverviewRedirect() {
  redirect("/dashboard");
}
