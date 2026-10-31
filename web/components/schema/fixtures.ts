// Test fixtures mirroring specs served by api/app/ui_schemas (shape checked by tsc).
import type { UiSpec } from "./types";

export const registerSpec: UiSpec = {
  name: "register",
  title: "Create your account",
  submit: { method: "POST", path: "/auth/register" },
  submit_label: "Create account",
  success_message: "Account created",
  schema: {
    type: "object",
    properties: {
      f_name: { type: "string", title: "First name", minLength: 1, maxLength: 50 },
      email: { type: "string", title: "Email", format: "email" },
      password: { type: "string", title: "Password", format: "password", minLength: 8 },
      experience_level: { type: "string", title: "Experience", enum: ["Beginner", "Expert"] },
    },
    required: ["f_name", "email", "password"],
  },
  ui: { order: ["f_name", "email", "password", "experience_level"], fields: {} },
};

export const skillAddSpec: UiSpec = {
  name: "skill_add",
  title: "Add a skill",
  submit: { method: "PUT", path: "/users/me/skills/{s_id}" },
  submit_label: "Add skill",
  success_message: "Skill saved",
  schema: {
    type: "object",
    properties: {
      s_id: { type: "integer", title: "Skill" },
      level: { type: "string", title: "Proficiency", enum: ["Beginner", "Expert"] },
    },
    required: ["s_id", "level"],
  },
  ui: { order: ["s_id", "level"], fields: {} },
};
