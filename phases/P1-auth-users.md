# P1 — Auth, roles, profiles & skills

| | |
|---|---|
| **Rubric** | 10 Next.js (3), 11 API + DB integration (2), 12 auth + roles + RBAC (4) |
| **Depends on** | P0 |
| **Agents** | `builder` |
| **Skills** | `scaffold`, `schema-form`, `gen-types`, `rule-tests` |
| **Branch** | `p1-auth-users` |
| **Spec** | `IMPLEMENTATION.md` §6 (auth/RBAC), §7.3–7.4 (renderers, client), §8 (endpoints), §4.1 D1/D4/D5/D6 |

## Goal
A user can register, log in, edit their profile and manage skills. Admin vs member is enforced in Next.js middleware, FastAPI and the MySQL grants. `SchemaForm` exists and drives every form in this phase.

## Tasks

### API
- [ ] `app/auth.py`: bcrypt hashing, JWT `{sub, role, exp}`, `current_user` and `require_role("admin")` dependencies; reject `is_active = FALSE` users.
- [ ] `plop router auth`: `POST /auth/register` (`CALL register_user`), `POST /auth/login`, `GET /auth/me`.
- [ ] `plop router users`:
  - `GET/PATCH /users/me`. The PATCH updates only the column-granted fields; trying `role` must hit a 1143 error that is mapped to 403.
  - `GET /users/{id}`.
  - `PUT /users/me/skills` (D1 multi-row), `PUT /users/me/skills/{s_id}` (D6 upsert), `DELETE …/{s_id}` (D5).
  - `POST /users/me/deactivate` (D4 via `deactivate_user`).
- [ ] `plop router skills`: `GET /skills?q=&category=`.
- [ ] `plop router admin`: `POST/PATCH /admin/skills` (`create_skill`/`update_skill`), `GET /admin/users`, `PUT /admin/users/{id}/role` (`set_user_role`). All behind `require_role("admin")`, and the procedures also check `fn_is_admin`.
- [ ] `app/ui_schemas/`: `login`, `register`, `profile_edit`, `skill_add`, `skill_admin`.
- [ ] `app/graph/sync.py` stubs `upsert_user`, `upsert_user_skills`, called after successful writes (wrapped in try/log). The bodies are filled in P6.

### Web
- [ ] Run `gen-types`; add `lib/api/client.ts` and `lib/api/server.ts` (`serverApi()` reads the cookie).
- [ ] `app/api/session/route.ts` (login sets an httpOnly cookie; DELETE logs out) and `app/api/proxy/[...path]/route.ts`.
- [ ] `middleware.ts`: verify the JWT with `jose`; guard `/dashboard`, `/graph`, `/analytics`, `/projects/*/manage`; allow `/admin` only for the admin role.
- [ ] `components/schema/`: `SchemaForm`, `buildZod`, `FieldRenderer`, `useSpec`, plus fields Text, Textarea, Number, Select, Date, Checkbox, Tags, Password, SkillLevel. Each file ≤ 150 lines.
- [ ] Pages (`plop page`): `/login`, `/register`, `/dashboard` (profile tab), `/dashboard/skills`, `/admin/skills`, `/admin/users`.
- [ ] Shell: a top nav with the user menu (`dropdown-menu`, `avatar`) that shows the admin link only for admins; `sonner` toasts for API errors.

### Tests
- [ ] `test_auth.py`: register, login, duplicate email → 409, deactivated user can't log in.
- [ ] `test_users_skills.py`: D1/D5/D6; `Python` vs ` python` → 409 on admin create.
- [ ] `test_rbac.py`:
  - Member on `/admin/*` → 403.
  - As raw `tt_app`: `UPDATE Users SET role='admin'` → 1143, `INSERT INTO Skill` → 1142.
  - `set_user_role` by a non-admin → `NOT_ADMIN`.
  - Demoting the last admin is blocked.
- [ ] `web`: a vitest middleware test (anonymous → `/login`, member on `/admin` → `/dashboard`), plus a `SchemaForm` render and validation test per spec.

## Done when
Register → login → add skills → edit profile works in the browser. An admin can add a skill; a member can't, and is stopped at all three layers. The gate in `phases/README.md` passes.

## Demo
1. Log in as a member and try `/admin`: you get redirected.
2. Call the API directly: 403.
3. Run the raw SQL as `tt_app`: 1142.
4. Log in as admin and add a skill.
