"""MySQL reads that feed the graph projection (kept apart so sync.py stays small)."""
from app import db

USER = """SELECT id, CONCAT(f_name, ' ', l_name) AS name, availability, is_active, bio FROM Users WHERE id = %s"""
USER_SKILLS = """SELECT h.s_id, s.s_name, h.u_s_level, fn_level_ord(h.u_s_level) AS level
                   FROM user_has_skill h JOIN Skill s ON s.s_id = h.s_id WHERE h.u_id = %s"""
SKILL = "SELECT s_id, s_name, category FROM Skill WHERE s_id = %s"
PROJECT = "SELECT p_id, owner_id, p_name, description, status FROM Project WHERE p_id = %s"
DOMAINS = "SELECT d_name FROM Domain WHERE project_id = %s ORDER BY d_name"
REQS = """SELECT r.s_id, s.s_name, r.req_role AS role, fn_level_ord(r.p_s_level) AS level, r.req_count AS count
            FROM Requires r JOIN Skill s ON s.s_id = r.s_id WHERE r.p_id = %s"""
# One row per user across their join/leave history: active if any row is active,
# role from the active row (else the latest past role).
MEMBERS = """SELECT j.u_id, MAX(j.leave_date IS NULL) AS active,
       COALESCE(MAX(CASE WHEN j.leave_date IS NULL THEN j.role END),
                SUBSTRING_INDEX(GROUP_CONCAT(j.role ORDER BY j.j_id DESC), ',', 1)) AS role
  FROM Joins j JOIN Team t ON t.t_id = j.t_id WHERE t.p_id = %s GROUP BY j.u_id"""
# Q11 [SELF-JOIN] pairs of users who have shared a team (history included), restricted to given users
PAIRS = """SELECT LEAST(a.u_id, b.u_id) AS u1, GREATEST(a.u_id, b.u_id) AS u2, COUNT(DISTINCT a.t_id) AS shared_teams
             FROM Joins a JOIN Joins b ON a.t_id = b.t_id AND a.u_id < b.u_id
            WHERE a.u_id IN ({ids}) OR b.u_id IN ({ids})
            GROUP BY u1, u2"""


async def user(user_id: int) -> dict | None:
    row = await db.fetch_one(USER, (user_id,))
    if row:
        row["skills"] = await db.fetch_all(USER_SKILLS, (user_id,))
    return row


async def project(p_id: int) -> dict | None:
    row = await db.fetch_one(PROJECT, (p_id,))
    if row:
        row["domains"] = [d["d_name"] for d in await db.fetch_all(DOMAINS, (p_id,))]
        row["reqs"] = await db.fetch_all(REQS, (p_id,))
        row["skills"] = sorted({r["s_name"] for r in row["reqs"]})
    return row


async def pairs_for(user_ids: list[int]) -> list[dict]:
    if not user_ids:
        return []
    ph = ", ".join(["%s"] * len(user_ids))
    return await db.fetch_all(PAIRS.format(ids=ph), (*user_ids, *user_ids))
