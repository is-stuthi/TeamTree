"""Cypher READS for the graph router (rubric 9: R). Mirrored in graph/003_demo_queries.cypher."""

# Collaboration edges within `depth` hops of the user (degrees are computed in Python)
NETWORK_EDGES = """MATCH p = (me:User {id: $uid})-[:COLLABORATED_WITH*1..2]-(:User)
WHERE length(p) <= $depth AND all(n IN nodes(p) WHERE n.active)
UNWIND relationships(p) AS r
RETURN DISTINCT startNode(r).id AS source, endNode(r).id AS target, r.shared AS shared"""

NAMES = """MATCH (u:User) WHERE u.id IN $ids RETURN u.id AS id, u.name AS name"""

RECOMMENDED = """MATCH (me:User {id: $uid})-[:COLLABORATED_WITH]-(mid:User)-[:COLLABORATED_WITH]-(c:User)
WHERE c <> me AND c.active AND NOT (me)-[:COLLABORATED_WITH]-(c)
WITH me, c, count(DISTINCT mid) AS mutual
OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill) WHERE NOT (me)-[:HAS_SKILL]->(s)
WITH me, c, mutual, collect(DISTINCT s.name) AS skills
OPTIONAL MATCH (:User)-[e:ENDORSES]->(c)
RETURN c.id AS id, c.name AS name, mutual, skills[..5] AS complementary_skills,
       coalesce(avg(e.weight), 0.0) AS endorsement_score
ORDER BY mutual DESC, size(complementary_skills) DESC, name LIMIT 10"""

PATH = """MATCH (a:User {id: $src}), (b:User {id: $dst})
OPTIONAL MATCH p = shortestPath((a)-[:COLLABORATED_WITH*..6]-(b))
RETURN [n IN coalesce(nodes(p), []) | {id: n.id, name: n.name}] AS path, length(p) AS hops"""

RELATED = """MATCH (s:Skill {id: $sid})
CALL (s) {
  MATCH (s)-[r:RELATED_TO]-(rel:Skill)
  WITH rel, r ORDER BY r.weight DESC, rel.name
  RETURN collect({id: rel.id, name: rel.name, weight: r.weight}) AS curated
}
CALL (s) {
  MATCH (s)<-[:HAS_SKILL]-(u:User)-[:HAS_SKILL]->(co:Skill) WHERE co <> s AND u.active
  WITH co, count(DISTINCT u) AS together WHERE together >= 2
  ORDER BY together DESC, co.name LIMIT 5
  RETURN collect({id: co.id, name: co.name, together: together}) AS co_occurring
}
RETURN curated, co_occurring"""

# Users (active, not on the team) holding a gap skill directly or via RELATED_TO, ranked by endorsements
GAP_CANDIDATES = """UNWIND $skills AS gap
MATCH (g:Skill {id: gap})
MATCH (u:User)-[:HAS_SKILL]->(have:Skill)
WHERE u.active AND (have = g OR (have)-[:RELATED_TO]-(g))
  AND NOT (u)-[:MEMBER_OF {active: true}]->(:Project {id: $pid})
OPTIONAL MATCH (:User)-[e:ENDORSES {skill_id: have.id}]->(u)
RETURN g.name AS skill, u.id AS user_id, u.name AS name, have.name AS via, have <> g AS related,
       coalesce(avg(e.weight), 0.0) AS endorsements
ORDER BY skill, related, endorsements DESC, name"""

SEARCH_PROJECTS = """CALL db.index.vector.queryNodes('project_embedding', $k, $vec) YIELD node, score
WHERE node.status = 'Open'
RETURN node.id AS id, node.name AS name, score ORDER BY score DESC LIMIT $limit"""

SIMILAR_PROJECTS = """MATCH (p:Project {id: $id}) WHERE p.embedding IS NOT NULL
CALL db.index.vector.queryNodes('project_embedding', $k, p.embedding) YIELD node, score
WHERE node <> p RETURN node.id AS id, node.name AS name, score ORDER BY score DESC LIMIT $limit"""

SIMILAR_USERS = """MATCH (u:User {id: $id}) WHERE u.embedding IS NOT NULL
CALL db.index.vector.queryNodes('user_embedding', $k, u.embedding) YIELD node, score
WHERE node <> u AND node.active RETURN node.id AS id, node.name AS name, score ORDER BY score DESC LIMIT $limit"""

ENDORSEMENTS = """MATCH (a:User)-[e:ENDORSES]->(:User {id: $id})
MATCH (s:Skill {id: e.skill_id})
RETURN s.id AS skill_id, s.name AS skill, count(e) AS count, avg(e.weight) AS avg_weight,
       collect(a.name) AS endorsers, collect(a.id) AS endorser_ids ORDER BY avg_weight DESC, skill"""

RELATIONS = """MATCH (a:Skill)-[r:RELATED_TO]->(b:Skill)
RETURN a.id AS a, a.name AS a_name, b.id AS b, b.name AS b_name, r.weight AS weight ORDER BY a_name, b_name"""
