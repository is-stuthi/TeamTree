# P5 — Skill matching & skill gap

| | |
|---|---|
| **Rubric** | 7 queries (4: nested IN, NOT EXISTS / relational division, correlated scalar) |
| **Depends on** | P4 |
| **Agents** | `builder` |
| **Skills** | `scaffold`, `schema-form`, `rule-tests`, `dataviz` |
| **Branch** | `p5-matching` |
| **Spec** | `IMPLEMENTATION.md` §3.5 (`SkillGap`), §4.2 Q3/Q4/Q7, §8 (matching weights), design doc §10 |

## Goal
Owners see ranked candidates with a transparent score breakdown, and a skill-gap report for their team. Profiles show each user's strongest skill.

## Tasks

### API (`plop router matching`)
- [ ] `app/services/matching.py` (≤ 150 lines): pure function `score(candidate, requirements, project_domains) -> {score, breakdown, missing_skills}`. Weights: coverage 50, proficiency 20, experience 15, domain 10, availability 5.
- [ ] `GET /projects/{id}/candidates?full=0|1&limit=`:
  - `full=0` prefilters with **Q3** (nested IN).
  - `full=1` uses **Q4** (NOT EXISTS relational division: users meeting every requirement).
  - Either way, exclude the owner, active members and pending applicants, then score in Python.
- [ ] `GET /projects/{id}/skill-gap` → `SkillGap` view.
- [ ] `GET /users/{id}` gains `strongest_skill` via **Q7** (correlated scalar subquery).
- [ ] Optional "Invite to apply" action: just a deep link to the project page. There is no new table.

### Web
- [ ] `/projects/[id]/manage/candidates`: a table of candidates with a score `Progress` bar, an expandable breakdown (five factor bars), missing-skill `Badge`s, and an "indicative score" note. Toggle "only fully qualified" (Q4).
- [ ] `/projects/[id]/manage/gap`: `SchemaDashboard` spec `specs/dashboards/skill_gap.json` with a table (shortfall highlighted) and a bar of required vs qualified. This phase builds the minimal `SchemaDashboard` with `table` and `bar` widgets; P7 adds the rest.

### SQL catalogue
- [ ] Append **Q3**, **Q4** and **Q7** with labels.

### Tests (`test_matching.py`)
- [ ] `score()` unit tests: the breakdown sums to the score; a candidate with no required skills gets coverage 0; Unavailable gets availability 0; proficiency is capped at 1.
- [ ] Q4 on seed returns exactly the users hand-verified as fully qualified.
- [ ] `/skill-gap` reports the seeded gap project's missing skill with the right `shortfall`, and the shortfall drops to 0 after accepting a qualified applicant.

## Done when
The candidates and gap tabs work on seed data and the numbers are explainable by hand. The gate passes.

## Demo
Open the gap project: Docker shortfall is 1. Open Candidates, toggle "fully qualified" (Q4), accept that person, and watch the gap close.
