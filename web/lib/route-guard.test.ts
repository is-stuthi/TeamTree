import { describe, expect, it } from "vitest";
import { guard, safeNext } from "./route-guard";
import type { Session } from "./session";

const member: Session = { userId: 3, role: "member", name: "Bob Mehta" };
const admin: Session = { userId: 1, role: "admin", name: "Admin User" };

describe("guard", () => {
  it("lets anyone see public pages", () => {
    expect(guard("/", null)).toBeNull();
    expect(guard("/projects", null)).toBeNull();
    expect(guard("/projects/4", null)).toBeNull();
  });

  it("sends anonymous users to login with a return path", () => {
    expect(guard("/dashboard/skills", null)).toBe("/login?next=%2Fdashboard%2Fskills");
    expect(guard("/projects/4/manage/team", null)).toBe("/login?next=%2Fprojects%2F4%2Fmanage%2Fteam");
  });

  it("keeps members out of admin pages", () => {
    expect(guard("/admin/users", member)).toBe("/dashboard");
    expect(guard("/admin/users", admin)).toBeNull();
    expect(guard("/dashboard", member)).toBeNull();
  });

  it("sends logged-in users away from login/register", () => {
    expect(guard("/login", member)).toBe("/dashboard");
    expect(guard("/register", admin)).toBe("/dashboard");
  });
});

describe("safeNext", () => {
  it("only allows same-site relative paths", () => {
    expect(safeNext("/dashboard/skills")).toBe("/dashboard/skills");
    expect(safeNext("https://evil.example")).toBe("/dashboard");
    expect(safeNext("//evil.example")).toBe("/dashboard");
    expect(safeNext(undefined)).toBe("/dashboard");
  });
});
