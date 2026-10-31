// =========================================================
// Vector indexes (rubric 4). 384 dims = sentence-transformers/all-MiniLM-L6-v2.
// Semantic project search and "similar users/projects" query these (P6).
// =========================================================
CREATE VECTOR INDEX project_embedding IF NOT EXISTS
FOR (p:Project) ON p.embedding
OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } };

CREATE VECTOR INDEX user_embedding IF NOT EXISTS
FOR (u:User) ON u.embedding
OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } };
