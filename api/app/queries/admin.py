"""SQL for the admin router."""

USERS = """SELECT id, CONCAT(f_name, ' ', l_name) AS name, email, role, is_active, created_at
             FROM Users ORDER BY is_active DESC, role, l_name, f_name"""

USER = """SELECT id, CONCAT(f_name, ' ', l_name) AS name, email, role, is_active, created_at
            FROM Users WHERE id = %s"""
