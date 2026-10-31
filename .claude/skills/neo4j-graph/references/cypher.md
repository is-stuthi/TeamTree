# Cypher conventions and patterns (TeamTREE)

## Sync (idempotent upserts)
```cypher
// upsert_user
MERGE (u:User {id:$id}) SET u.name = $name, u.availability = $availability, u.active = $active;

// upsert_user_skills: replace the projection edges only
MATCH (u:User {id:$id})
OPTIONAL MATCH (u)-[old:HAS_SKILL]->() DELETE old
WITH u UNWIND $skills AS s
MATCH (k:Skill {id:s.id}) MERGE (u)-[r:HAS_SKILL]->(k) SET r.level = s.level;

// upsert_project (+ embedding)
MERGE (p:Project {id:$id})
SET p.name = $name, p.status = $status, p.domains = $domains, p.embedding = $embedding
WITH p MATCH (o:User {id:$owner}) MERGE (o)-[:OWNS]->(p);

// collaborator edges from SQL Q11 rows
UNWIND $pairs AS row
MATCH (a:User {id:row.u1}), (b:User {id:row.u2})
MERGE (a)-[c:COLLABORATED_WITH]-(b) SET c.shared = row.shared_teams;
```
Never `MERGE` a whole pattern with unbound nodes. Match or merge the nodes first, then merge the relationship.

## Graph-only writes (the rubric "U" and "D")
```cypher
// endorse (only if they collaborated)
MATCH (a:User {id:$from})-[:COLLABORATED_WITH]-(b:User {id:$to})
MERGE (a)-[e:ENDORSES {skill_id:$sid}]->(b)
SET e.weight = $weight, e.note = $note, e.at = datetime()
RETURN e;                                   // no row → API returns 409 NOT_COLLABORATORS

// remove endorsement
MATCH (:User {id:$from})-[e:ENDORSES {skill_id:$sid}]->(:User {id:$to}) DELETE e;

// related skills (admin)
MATCH (a:Skill {id:$a}), (b:Skill {id:$b}) MERGE (a)-[r:RELATED_TO]-(b) SET r.weight = $w;
MATCH (:Skill {id:$a})-[r:RELATED_TO]-(:Skill {id:$b}) DELETE r;
```

## Reads
```cypher
// shortest collaboration path
MATCH (a:User {id:$from}), (b:User {id:$to})
MATCH p = shortestPath((a)-[:COLLABORATED_WITH*..6]-(b))
RETURN [n IN nodes(p) | {id:n.id, name:n.name}] AS path, length(p) AS hops;

// related skills: curated edges + co-occurrence
MATCH (s:Skill {id:$sid})
OPTIONAL MATCH (s)-[r:RELATED_TO]-(rel:Skill)
WITH s, collect({id:rel.id, name:rel.name, weight:r.weight}) AS curated
OPTIONAL MATCH (s)<-[:HAS_SKILL]-(u:User)-[:HAS_SKILL]->(co:Skill) WHERE co <> s
WITH curated, co, count(u) AS together WHERE together >= 2
RETURN curated, collect({id:co.id, name:co.name, together:together})[..5] AS co_occurring;

// network for the force graph (nodes + edges JSON)
MATCH p = (u:User {id:$uid})-[:COLLABORATED_WITH*1..2]-(:User)
UNWIND relationships(p) AS r
WITH DISTINCT r
RETURN collect(DISTINCT {source:startNode(r).id, target:endNode(r).id, shared:r.shared}) AS edges;

// similar projects (vector)
MATCH (p:Project {id:$pid})
CALL db.index.vector.queryNodes('project_embedding', 6, p.embedding) YIELD node, score
WHERE node <> p RETURN node.id AS id, node.name AS name, score;
```

## Gotchas
- A vector index only covers nodes whose property is a `LIST<FLOAT>` of exactly 384 values. A wrong size is silently skipped.
- The relationship direction for `COLLABORATED_WITH` and `RELATED_TO` is arbitrary. Always match them undirected (`-[]-`).
- Variable-length patterns must be bounded (`*..6`) to keep queries fast.
- Pass numbers as ints from Python. A float id won't match an int id.
