// =========================================================
// Neo4j constraints and indexes (rubric 4). Idempotent.
// Applied by api/scripts/graph_init.py (see neo4j-graph skill).
// =========================================================
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name);
CREATE INDEX project_status IF NOT EXISTS FOR (p:Project) ON (p.status);
