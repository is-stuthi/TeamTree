"""Chen-notation ER for schema v2 -> docs/er_chen.dot (all nodes pinned; Graphviz neato).

    python docs/tools/gen_er_chen.py > docs/er_chen.dot
    neato -Tsvg docs/er_chen.dot -o docs/er_chen.svg      # or -Tpng -o "docs/ER Diagram.png"

Edit E/R/A below when the schema changes; docs/er.mmd is the crow's-foot twin."""
import sys

NEW = "#b45309"   # attributes added in schema v2
E = {  # entity: (x, y)
    "USERS": (0, 0), "PROJECT": (15, 0), "APPLICATION": (7.5, 7),
    "SKILL": (7.5, -6.5), "TEAM": (7.5, 14), "TASK": (7.5, -14),
}
# relationship: (x, y, [(entity, cardinality, total?, role)], [attributes])
R = {
    "SUBMITS":     (2.6, 4.2, [("USERS", "1", 0, ""), ("APPLICATION", "N", 1, "")], []),
    "REVIEWS":     (5.0, 2.2, [("USERS", "1", 0, "owner"), ("APPLICATION", "N", 0, "")], ["decision_date"]),
    "RECEIVES":    (11.8, 3.8, [("PROJECT", "1", 0, ""), ("APPLICATION", "N", 1, "")], []),
    "CREATES_OWNS": (10.2, 0.6, [("USERS", "1", 0, ""), ("PROJECT", "N", 1, "")], []),
    "TRANSFERS":   (9.4, -2.2, [("PROJECT", "N", 0, ""), ("USERS", "1", 0, "from"), ("USERS", "1", 0, "to")],
                    ["transferred_at"]),
    "HAS":         (2.6, -3.6, [("USERS", "M", 0, ""), ("SKILL", "N", 0, "")], ["u_s_level"]),
    "REQUIRES":    (12.4, -3.6, [("PROJECT", "M", 0, ""), ("SKILL", "N", 0, "")],
                    ["p_s_level", "req_role", "req_count"]),
    "JOINS":       (0, 10.5, [("USERS", "M", 0, ""), ("TEAM", "N", 1, "")],
                    ["role", "join_date", "leave_date*"]),
    "HAS_TEAM":    (15, 10.5, [("PROJECT", "1", 1, ""), ("TEAM", "1", 1, "")], []),
    "ASSIGNED_TO": (0, -10.5, [("USERS", "1", 0, ""), ("TASK", "N", 0, "")], []),
    "CONTAINS":    (15, -10.5, [("PROJECT", "1", 0, ""), ("TASK", "N", 1, "")], []),
    "SUBTASK_OF":  (7.5, -18.5, [("TASK", "1", 0, "parent"), ("TASK", "N", 0, "subtask")], []),
}
# entity attributes: name, kind (key | multi | derived | composite:<parts> | plain), new?
A = {
    "USERS": [("id", "key"), ("name", "composite:f_name,m_name,l_name"), ("email", ""), ("password_hash", ""),
              ("role*", ""), ("bio", ""), ("location", ""), ("u_photo", ""), ("dob", ""), ("age", "derived"),
              ("experience_level", ""), ("availability", ""), ("is_active*", ""), ("created_at", "")],
    "PROJECT": [("p_id", "key"), ("p_name", ""), ("description", ""), ("deadline", ""), ("status", ""),
                ("max_team_size*", ""), ("creation_date", ""), ("domain", "multi")],
    "SKILL": [("s_id", "key"), ("s_name", ""), ("category", "")],
    "APPLICATION": [("a_id", "key"), ("msg", ""), ("status*\\n(+ Withdrawn)", ""), ("a_date", "")],
    "TEAM": [("t_id", "key"), ("team_name", ""), ("create_date", "")],
    "TASK": [("task_id", "key"), ("t_name", ""), ("description", ""), ("status", ""), ("priority", ""),
             ("due_date", ""), ("created_at", "")],
}

out = ['graph ER {',
       '  layout=neato; overlap=true; splines=false; outputorder=edgesfirst;',
       '  bgcolor=white; pad=0.4; fontname="Helvetica";',
       '  node [fontname="Helvetica", fontsize=11, style=filled, fillcolor=white];',
       '  edge [fontname="Helvetica", fontsize=12, len=1.1];']
n = 0
import math
POS = {**E, **{r: v[:2] for r, v in R.items()}}
FAN = {"USERS": (108, 252, (2.6, 4.0)), "PROJECT": (-55, 75, (2.6, 3.9)), "APPLICATION": (35, 145, (2.0,)),
       "SKILL": (200, 340, (1.9,)), "TEAM": (40, 140, (1.9,)), "TASK": (15, 165, (2.2, 3.2)),
       "JOINS": (115, 245, (2.1,)), "REVIEWS": (150, 150, (1.6,)), "TRANSFERS": (270, 270, (1.3,)),
       "HAS": (215, 215, (1.8,)), "REQUIRES": (-75, 5, (2.2,))}


def attr(owner, name, kind, xy):
    global n
    n += 1
    nid, new = f"a{n}", name.endswith("*") or "*\\n" in name
    label = name.replace("*", "")
    color = f', color="{NEW}", fontcolor="{NEW}"' if new else ""
    if kind == "key":
        out.append(f'  {nid} [shape=ellipse, label=<<U>{label}</U>>{color}, pos="{xy[0]:.2f},{xy[1]:.2f}!"];')
    elif kind == "multi":
        out.append(f'  {nid} [shape=ellipse, peripheries=2, label="{label}"{color}, pos="{xy[0]:.2f},{xy[1]:.2f}!"];')
    elif kind == "derived":
        out.append(f'  {nid} [shape=ellipse, style="filled,dashed", label="{label}"{color}, pos="{xy[0]:.2f},{xy[1]:.2f}!"];')
    else:
        out.append(f'  {nid} [shape=ellipse, label="{label}"{color}, pos="{xy[0]:.2f},{xy[1]:.2f}!"];')
    out.append(f'  {owner} -- {nid};')
    if kind.startswith("composite:"):
        parts = kind.split(":", 1)[1].split(",")
        ox, oy = POS[owner]
        base = math.atan2(xy[1] - oy, xy[0] - ox)
        for i, part in enumerate(parts):
            a = base + (i - (len(parts) - 1) / 2) * 0.85
            attr(nid, part, "", (xy[0] + 1.9 * math.cos(a), xy[1] + 1.9 * math.sin(a)))


def fan(owner, items):
    a0, a1, radii = FAN[owner]
    ox, oy = POS[owner]
    k = len(items)
    for i, (name, kind) in enumerate(items):
        deg = math.radians(a0 if k == 1 else a0 + (a1 - a0) * i / (k - 1))
        r = radii[i % len(radii)]
        attr(owner, name, kind, (ox + r * math.cos(deg), oy + r * math.sin(deg)))


for e, (x, y) in E.items():
    out.append(f'  {e} [shape=box, penwidth=2, fontsize=14, label=<<B>{e}</B>>, pos="{x},{y}!"];')
for r, (x, y, ends, attrs) in R.items():
    label = r.replace("_", " / " if r == "CREATES_OWNS" else " ").replace("HAS TEAM", "HAS")
    out.append(f'  {r} [shape=diamond, fillcolor="#eef2ff", label="{label}", pos="{x},{y}!"];')
    for ent, card, total, role in ends:
        lab = f"{role} {card}".strip()
        port = {"from": ":e", "to": ":s", "parent": ":sw", "subtask": ":se"}.get(role, "")
        style = ', color="black:white:black", penwidth=1.2' if total else ""
        kind = "headlabel" if port else "label"
        extra = f", labeldistance=3.5, labelangle={-30 if role == 'to' else 25}" if port else ""
        out.append(f'  {r} -- {ent}{port} [{kind}="{lab}"{extra}{style}];')
    if attrs:
        fan(r, [(a, "") for a in attrs])
for e, attrs in A.items():
    fan(e, attrs)

out.append('  legend [shape=plaintext, pos="-6,-18!", label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="4" BGCOLOR="white">'
           '<TR><TD COLSPAN="2"><B>TeamTREE ER (schema v2, Chen notation)</B></TD></TR>'
           '<TR><TD ALIGN="LEFT">Rectangle</TD><TD ALIGN="LEFT">entity</TD></TR>'
           '<TR><TD ALIGN="LEFT">Diamond</TD><TD ALIGN="LEFT">relationship</TD></TR>'
           '<TR><TD ALIGN="LEFT"><U>underlined</U></TD><TD ALIGN="LEFT">key attribute</TD></TR>'
           '<TR><TD ALIGN="LEFT">double ellipse</TD><TD ALIGN="LEFT">multivalued (domain)</TD></TR>'
           '<TR><TD ALIGN="LEFT">dashed ellipse</TD><TD ALIGN="LEFT">derived (age from dob)</TD></TR>'
           '<TR><TD ALIGN="LEFT">ellipse with sub-ellipses</TD><TD ALIGN="LEFT">composite (name)</TD></TR>'
           '<TR><TD ALIGN="LEFT">double line</TD><TD ALIGN="LEFT">total participation</TD></TR>'
           '<TR><TD ALIGN="LEFT">single line</TD><TD ALIGN="LEFT">partial participation</TD></TR>'
           '<TR><TD ALIGN="LEFT">1 / N / M</TD><TD ALIGN="LEFT">cardinality</TD></TR>'
           f'<TR><TD ALIGN="LEFT"><FONT COLOR="{NEW}">orange</FONT></TD><TD ALIGN="LEFT">new in v2</TD></TR>'
           '</TABLE>>];')
out.append("}")
sys.stdout.write("\n".join(out) + "\n")
