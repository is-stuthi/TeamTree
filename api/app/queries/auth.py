"""SQL for the auth router."""

CREDENTIALS = """SELECT id, password_hash, is_active, role, CONCAT(f_name, ' ', l_name) AS name
                   FROM Users WHERE email = LOWER(TRIM(%s))"""
