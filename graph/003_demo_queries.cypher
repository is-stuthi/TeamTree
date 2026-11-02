// =========================================================
// Demo Cypher for the viva (rubric 4 + 9). Paste into the Neo4j Browser
// (http://localhost:7474) one statement at a time. Same queries as
// api/app/queries/graph.py and graph_write.py, with literal parameters.
// =========================================================

// ---- Creation (rubric 4): schema objects ----
SHOW CONSTRAINTS;
SHOW VECTOR INDEXES;

// ---- READ: collaboration network around Farhan (id 7), 2 hops (visual in the Browser) ----
MATCH p = (:User {id: 7})-[:COLLABORATED_WITH*1..2]-(:User) RETURN p;

// ---- READ: recommended collaborators (friends of collaborators, complementary skills) ----
MATCH (me:User {id: 7})-[:COLLABORATED_WITH]-(mid:User)-[:COLLABORATED_WITH]-(c:User)
WHERE c <> me AND c.active AND NOT (me)-[:COLLABORATED_WITH]-(c)
WITH me, c, count(DISTINCT mid) AS mutual
OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill) WHERE NOT (me)-[:HAS_SKILL]->(s)
RETURN c.name AS candidate, mutual, collect(DISTINCT s.name)[..5] AS complementary_skills
ORDER BY mutual DESC;

// ---- READ: shortest collaboration path between Esha (6) and Liam (13) ----
MATCH (a:User {id: 6}), (b:User {id: 13})
MATCH p = shortestPath((a)-[:COLLABORATED_WITH*..6]-(b))
RETURN [n IN nodes(p) | n.name] AS path, length(p) AS hops;

// ---- READ: skills related to Docker (curated) + co-occurring skills ----
MATCH (s:Skill {id: 16})-[r:RELATED_TO]-(rel:Skill) RETURN rel.name AS related, r.weight AS weight ORDER BY weight DESC;
MATCH (s:Skill {id: 16})<-[:HAS_SKILL]-(u:User)-[:HAS_SKILL]->(co:Skill)
WHERE co <> s RETURN co.name AS skill, count(DISTINCT u) AS together ORDER BY together DESC LIMIT 5;

// ---- READ (vector): projects similar to Plant Disease Classifier (cosine on 384-dim embeddings) ----
MATCH (p:Project {id: 1})
CALL db.index.vector.queryNodes('project_embedding', 5, p.embedding) YIELD node, score
WHERE node <> p RETURN node.name AS project, round(score, 3) AS similarity;
// (free-text search embeds the query in the API: GET /graph/search/projects?q=...)

// ---- UPDATE: Alice (2) endorses Gauri (8) for UI/UX (21); only collaborators can ----
MATCH (a:User {id: 2})-[:COLLABORATED_WITH]-(b:User {id: 8})
MERGE (a)-[e:ENDORSES {skill_id: 21}]->(b)
SET e.weight = 3, e.note = 'Lovely UI', e.at = datetime() RETURN e;

// ---- UPDATE: change the endorsement strength ----
MATCH (:User {id: 2})-[e:ENDORSES {skill_id: 21}]->(:User {id: 8}) SET e.weight = 5 RETURN e.weight;

// ---- UPDATE: curate a skill relation (admin feature) ----
MATCH (a:Skill {id: 2}), (b:Skill {id: 4}) MERGE (a)-[r:RELATED_TO]->(b) SET r.weight = 0.4 RETURN r;

// ---- DELETE: remove the endorsement and the relation ----
MATCH (:User {id: 2})-[e:ENDORSES {skill_id: 21}]->(:User {id: 8}) DELETE e;
MATCH (:Skill {id: 2})-[r:RELATED_TO]-(:Skill {id: 4}) DELETE r;

// ---- Sanity: what's in the graph ----
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY label;
MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS n ORDER BY rel;
