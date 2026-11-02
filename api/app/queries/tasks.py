"""SQL for tasks. Inserts/updates are validated by trg_task_bi / trg_task_bu
(assignee must be an active member, due date within the deadline, parent in
the same project, no tasks on finished projects)."""

_COLS = """tk.task_id, tk.p_id, tk.u_id, CONCAT(u.f_name, ' ', u.l_name) AS assignee_name,
       tk.parent_task_id, tk.t_name, tk.description, tk.status, tk.priority, tk.due_date,
       (tk.due_date IS NOT NULL AND tk.due_date < CURDATE() AND tk.status <> 'Done') AS is_overdue"""

LIST = f"""SELECT {_COLS} FROM Task tk LEFT JOIN Users u ON u.id = tk.u_id
            WHERE tk.p_id = %s ORDER BY tk.status = 'Done', tk.due_date IS NULL, tk.due_date, tk.task_id"""

ONE = f"SELECT {_COLS} FROM Task tk LEFT JOIN Users u ON u.id = tk.u_id WHERE tk.task_id = %s"

MINE = f"""SELECT {_COLS}, p.p_name FROM Task tk
             JOIN Project p ON p.p_id = tk.p_id
             LEFT JOIN Users u ON u.id = tk.u_id
            WHERE tk.u_id = %s
            ORDER BY tk.status = 'Done', tk.due_date IS NULL, tk.due_date"""

INSERT = """INSERT INTO Task (p_id, u_id, parent_task_id, t_name, description, priority, due_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

PROJECT_OF = "SELECT p_id FROM Task WHERE task_id = %s"

PATCH_COLUMNS = ("t_name", "description", "status", "priority", "due_date")
NOT_NULL_COLUMNS = {"t_name", "status", "priority"}

# Q8 [RECURSIVE CTE] subtask tree with depth and breadcrumb path
TREE = """WITH RECURSIVE tree AS (
    SELECT task_id, 0 AS depth, CAST(t_name AS CHAR(1000)) AS path,
           CAST(LPAD(task_id, 8, '0') AS CHAR(1000)) AS sort_key
      FROM Task WHERE p_id = %s AND parent_task_id IS NULL
    UNION ALL
    SELECT c.task_id, tree.depth + 1, CONCAT(tree.path, ' › ', c.t_name),
           CONCAT(tree.sort_key, '/', LPAD(c.task_id, 8, '0'))
      FROM Task c JOIN tree ON c.parent_task_id = tree.task_id
)
SELECT """ + _COLS + """, tree.depth, tree.path
  FROM tree
  JOIN Task tk ON tk.task_id = tree.task_id
  LEFT JOIN Users u ON u.id = tk.u_id
 ORDER BY tree.sort_key"""


def patch(fields: list[str]) -> str:
    cols = [f for f in fields if f in PATCH_COLUMNS]
    return "UPDATE Task SET " + ", ".join(f"{c} = %s" for c in cols) + " WHERE task_id = %s"
