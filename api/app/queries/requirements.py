"""SQL for project skill requirements (PROJECT -REQUIRES-> SKILL)."""

UPSERT = """INSERT INTO Requires (p_id, s_id, req_role, p_s_level, req_count)
            VALUES (%s, %s, %s, %s, %s) AS new
            ON DUPLICATE KEY UPDATE p_s_level = new.p_s_level, req_count = new.req_count"""

DELETE = "DELETE FROM Requires WHERE p_id = %s AND s_id = %s AND req_role = %s"

# D2 [INSERT ... SELECT] copy another project's requirements ("use as template")
COPY_FROM = """INSERT INTO Requires (p_id, s_id, req_role, p_s_level, req_count)
               SELECT %s, src.s_id, src.req_role, src.p_s_level, src.req_count
                 FROM Requires src WHERE src.p_id = %s
               ON DUPLICATE KEY UPDATE p_s_level = src.p_s_level, req_count = src.req_count"""
