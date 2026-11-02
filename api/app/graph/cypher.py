"""Cypher for the MySQL -> Neo4j projection (idempotent MERGE). Sync never touches
graph-only data (ENDORSES, RELATED_TO). Always parameterised."""

UPSERT_SKILL = """MERGE (s:Skill {id: $id}) SET s.name = $name, s.category = $category"""

UPSERT_USER = """MERGE (u:User {id: $id})
SET u.name = $name, u.availability = $availability, u.active = $active, u.embedding = $embedding"""

DEACTIVATE_USER = """MATCH (u:User {id: $id}) SET u.active = false
WITH u OPTIONAL MATCH (u)-[m:MEMBER_OF]->() SET m.active = false"""

REPLACE_USER_SKILLS = """MATCH (u:User {id: $id})
OPTIONAL MATCH (u)-[old:HAS_SKILL]->() DELETE old
WITH DISTINCT u UNWIND $skills AS s
MATCH (k:Skill {id: s.s_id}) MERGE (u)-[r:HAS_SKILL]->(k) SET r.level = s.level"""

UPSERT_PROJECT = """MERGE (p:Project {id: $id})
SET p.name = $name, p.status = $status, p.domains = $domains, p.embedding = $embedding
WITH p OPTIONAL MATCH (:User)-[o:OWNS]->(p) DELETE o
WITH DISTINCT p MATCH (owner:User {id: $owner}) MERGE (owner)-[:OWNS]->(p)"""

REPLACE_REQUIREMENTS = """MATCH (p:Project {id: $id})
OPTIONAL MATCH (p)-[old:REQUIRES]->() DELETE old
WITH DISTINCT p UNWIND $reqs AS r
MATCH (k:Skill {id: r.s_id}) MERGE (p)-[q:REQUIRES {role: r.role}]->(k) SET q.level = r.level, q.count = r.count"""

REPLACE_MEMBERS = """MATCH (p:Project {id: $id})
OPTIONAL MATCH (:User)-[old:MEMBER_OF]->(p) DELETE old
WITH DISTINCT p UNWIND $members AS m
MATCH (u:User {id: m.u_id}) MERGE (u)-[r:MEMBER_OF]->(p) SET r.role = m.role, r.active = m.active"""

UPSERT_COLLABORATIONS = """UNWIND $pairs AS row
MATCH (a:User {id: row.u1}), (b:User {id: row.u2})
MERGE (a)-[c:COLLABORATED_WITH]-(b) SET c.shared = row.shared_teams"""

SET_MEMBER_INACTIVE = """MATCH (:User {id: $u})-[m:MEMBER_OF]->(:Project {id: $p}) SET m.active = false"""

SET_PROJECT_EMBEDDING = """MATCH (p:Project {id: $id}) SET p.embedding = $embedding RETURN p.id AS id"""

COUNTS = """CALL () { MATCH (n) RETURN count(n) AS nodes }
CALL () { MATCH ()-[r]->() RETURN count(r) AS rels }
RETURN nodes, rels"""
