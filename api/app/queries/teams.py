"""SQL for teams. Membership changes go through procedures (remove_member,
leave_team, transfer_ownership); tt_app cannot write Joins directly."""

MEMBERS = """SELECT tm.j_id, tm.u_id, tm.member_name, tm.email, tm.role, tm.join_date, tm.leave_date,
       tm.is_active,
       (SELECT COUNT(*) FROM Task tk WHERE tk.p_id = tm.p_id AND tk.u_id = tm.u_id
                                       AND tk.status <> 'Done') AS open_tasks
  FROM TeamMemberDetails tm
 WHERE tm.p_id = %(p)s AND (tm.is_active OR %(past)s)
 ORDER BY tm.is_active DESC, tm.role = 'Owner' DESC, tm.join_date"""

MY_TEAMS = """SELECT tm.p_id, p.p_name, tm.team_name, p.status, tm.role, tm.join_date,
       (p.owner_id = %(u)s) AS is_owner, fn_active_member_count(tm.p_id) AS team_size
  FROM TeamMemberDetails tm JOIN Project p ON p.p_id = tm.p_id
 WHERE tm.u_id = %(u)s AND tm.is_active
 ORDER BY is_owner DESC, p.status = 'Ongoing' DESC, tm.join_date DESC"""

# Q5 [CORRELATED] active members who completed more tasks than their team's average
TOP_CONTRIBUTORS = """SELECT j.u_id, CONCAT(u.f_name, ' ', u.l_name) AS member_name, COUNT(tk.task_id) AS done
  FROM Joins j
  JOIN Team t   ON t.t_id = j.t_id
  JOIN Users u  ON u.id = j.u_id
  JOIN Task tk  ON tk.p_id = t.p_id AND tk.u_id = j.u_id AND tk.status = 'Done'
 WHERE t.p_id = %s AND j.leave_date IS NULL
 GROUP BY t.t_id, t.p_id, j.u_id, u.f_name, u.l_name
HAVING COUNT(tk.task_id) > (
       SELECT COUNT(*) / NULLIF((SELECT COUNT(*) FROM Joins j2
                                  WHERE j2.t_id = t.t_id AND j2.leave_date IS NULL), 0)
         FROM Task t2
         JOIN Joins j3 ON j3.t_id = t.t_id AND j3.u_id = t2.u_id AND j3.leave_date IS NULL
        WHERE t2.p_id = t.p_id AND t2.status = 'Done')
 ORDER BY done DESC"""
