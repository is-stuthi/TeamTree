"""Cypher UPDATE / DELETE for graph-only data (rubric 9: U and D)."""

# Only between users who share(d) a team; no row back -> not collaborators.
ENDORSE = """MATCH (a:User {id: $src})-[:COLLABORATED_WITH]-(b:User {id: $dst})
MERGE (a)-[e:ENDORSES {skill_id: $sid}]->(b)
SET e.weight = $weight, e.note = $note, e.at = datetime()
RETURN e.weight AS weight"""

UNENDORSE = """MATCH (:User {id: $src})-[e:ENDORSES {skill_id: $sid}]->(:User {id: $dst})
DELETE e RETURN count(*) AS deleted"""

RELATE = """MATCH (a:Skill {id: $a}), (b:Skill {id: $b})
OPTIONAL MATCH (a)-[old:RELATED_TO]-(b) DELETE old
WITH a, b MERGE (a)-[r:RELATED_TO]->(b) SET r.weight = $weight RETURN r.weight AS weight"""

UNRELATE = """MATCH (:Skill {id: $a})-[r:RELATED_TO]-(:Skill {id: $b}) DELETE r RETURN count(*) AS deleted"""
