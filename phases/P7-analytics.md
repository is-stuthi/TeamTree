# P7 — Analytics & dashboards

| | |
|---|---|
| **Rubric** | 7 queries (4: GROUP BY/HAVING, recursive date series, CTE + window, UNION), 10 Next.js (3) |
| **Depends on** | P5, P6 |
| **Agents** | `sql-scout` drafts queries and dashboard JSON · `builder` wires them |
| **Skills** | `schema-form`, `dataviz`, `gen-types`, `rule-tests` |
| **Branch** | `p7-analytics` |
| **Spec** | `IMPLEMENTATION.md` §3.5 (views), §4.2 Q2/Q9/Q10/Q12, §7.3 (widgets), design doc §11 |

## Goal
Every metric in design doc §11 is visible on JSON-driven dashboards. All numbers come from SQL views and queries, never from frontend computation.

## Tasks

### API (`plop router analytics`)
- [ ] Use a second pool connected as **`tt_report`** (views only). This demonstrates the analyst role.
  - Queries that need base tables run on the `tt_app` pool: Q2, Q9, Q12.
  - Document the split in the router's docstring.
- [ ] `GET /analytics/skills`: `TopInDemandSkills` + **Q10** (top 3 per category, CTE + `RANK`).
- [ ] `GET /analytics/projects`: count by status and by domain, approaching deadlines, average duration, **Q2** (no applications).
- [ ] `GET /analytics/applications`: `ProjectApplicationSummary`, overall acceptance rate (decided only), average decision time, **Q9** (30-day series).
- [ ] `GET /analytics/users`: most active users (clearly labelled), projects created, applications submitted/accepted, tasks completed.
- [ ] `GET /analytics/teams`: average and largest team size, role distribution, `TaskProgressSummary`.
- [ ] `GET /users/me/activity` → **Q12** (UNION ALL feed).
- [ ] `GET /public/stats` (no auth): totals for the landing page.

### Web
- [ ] Complete `SchemaDashboard` widgets: `stat`, `pie`, `line`, `progress`, `graph` (P5 already built `table` and `bar`). Each is ≤ 150 lines and follows the `dataviz` skill for colours.
- [ ] Specs:
  - `specs/dashboards/analytics.json`: tabs for Skills, Projects, Applications, Users, Teams.
  - `public_stats.json` (landing).
  - `my_dashboard.json`: activity feed, my task progress, network mini-graph.
- [ ] `/analytics` page (admins see all tabs; members see Skills, Projects and Applications). `/` landing uses `public_stats`.
- [ ] `/dashboard` home renders `my_dashboard`.

### SQL catalogue
- [ ] Append **Q2**, **Q9**, **Q10**, **Q12** (and **Q11** from P6 if it's missing) with labels. The catalogue is now complete: Q1–Q12.

### Tests (`test_analytics.py`)
- [ ] The acceptance rate excludes Pending and Withdrawn (hand-computed from seed).
- [ ] Demand and supply counts match the seed for three named skills.
- [ ] Q9 returns exactly 30 rows, with zeros filled in.
- [ ] Q2 lists the seeded project that has no applications.
- [ ] As `tt_report`, `SELECT * FROM Users` → 1142; `SELECT * FROM TopInDemandSkills` works.

## Done when
`/analytics` shows every §11 metric. Adding a new chart only needs a JSON change. The gate passes.

## Demo
Add a widget to `analytics.json` live (no code change) and reload. Then show the `tt_report` denial on base tables.
