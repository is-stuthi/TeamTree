import { describe, expect, it } from "vitest";
import { buildZod, initialValues } from "./buildZod";
import { registerSpec, skillAddSpec } from "./fixtures";
import { buildQuery, buildRequest } from "./request";
import { formSchema } from "./types";

describe("buildZod", () => {
  const schema = buildZod(formSchema(registerSpec));

  it("accepts valid input and treats empty optional fields as absent", () => {
    const r = schema.safeParse({ f_name: "Zara", email: "z@x.io", password: "longenough", experience_level: "" });
    expect(r.success).toBe(true);
    expect(r.data).toEqual({ f_name: "Zara", email: "z@x.io", password: "longenough", experience_level: undefined });
  });

  it("reports required, format and length errors per field", () => {
    const r = schema.safeParse({ f_name: "", email: "nope", password: "short", experience_level: "Wizard" });
    const issues = Object.fromEntries((r.error?.issues ?? []).map((i) => [i.path[0], i.message]));
    expect(issues.f_name).toBe("Required");
    expect(issues.email).toBe("Enter a valid email");
    expect(issues.password).toBe("At least 8 characters");
    expect(issues.experience_level).toBe("Choose an option");
  });

  it("coerces integer fields coming from selects", () => {
    const r = buildZod(formSchema(skillAddSpec)).safeParse({ s_id: "11", level: "Expert" });
    expect(r.data).toEqual({ s_id: 11, level: "Expert" });
  });

  it("builds empty initial values, or the API record when editing", () => {
    expect(initialValues(formSchema(skillAddSpec))).toEqual({ s_id: "", level: "" });
    expect(initialValues(formSchema(skillAddSpec), { s_id: 3, level: null })).toEqual({ s_id: "3", level: "" });
  });
});

describe("buildRequest", () => {
  it("fills path placeholders and removes them from the body", () => {
    expect(buildRequest(skillAddSpec, { s_id: 11, level: "Expert" })).toEqual({
      url: "/api/proxy/users/me/skills/11", method: "PUT", body: { level: "Expert" },
    });
  });

  it("sends cleared fields as null on PATCH so they can be cleared", () => {
    const req = buildRequest({ ...registerSpec, submit: { method: "PATCH", path: "/users/me" } }, { f_name: "Z", bio: undefined });
    expect(req.body).toEqual({ f_name: "Z", bio: null });
  });

  it("turns search-form values into a query string, skipping empties", () => {
    expect(buildQuery({ q: "web", skill: 16, status: undefined, domain: "", tags: [] })).toBe("q=web&skill=16");
  });

  it("honours an action override (session login)", () => {
    const req = buildRequest(registerSpec, { f_name: "Z", nick: undefined }, { action: "/api/session?mode=register" });
    expect(req).toEqual({ url: "/api/session?mode=register", method: "POST", body: { f_name: "Z" } });
  });
});
