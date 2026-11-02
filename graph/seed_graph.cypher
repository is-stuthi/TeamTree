// =========================================================
// Graph-only seed data (not in MySQL): curated skill relations and endorsements.
// Loaded by `python scripts/sync_graph.py --full` after the MySQL projection.
// Endorsements are only between users who share(d) a team (COLLABORATED_WITH).
// =========================================================

UNWIND [
  [16, 17, 0.9], [16, 19, 0.6], [17, 18, 0.7], [6, 7, 0.9], [6, 5, 0.7], [7, 5, 0.8],
  [8, 5, 0.6], [1, 12, 0.7], [12, 14, 0.9], [13, 11, 0.7], [13, 1, 0.6], [21, 22, 0.9],
  [21, 25, 0.8], [20, 19, 0.7], [15, 11, 0.5], [10, 8, 0.6], [9, 6, 0.5]
] AS rel
MATCH (a:Skill {id: rel[0]}), (b:Skill {id: rel[1]})
MERGE (a)-[r:RELATED_TO]-(b) SET r.weight = rel[2];

UNWIND [
  [8, 5, 7, 5, 'Shipped the theme system with Next.js'],
  [5, 8, 5, 4, 'Clean, well-typed components'],
  [2, 8, 6, 4, 'Great React work on the journal app'],
  [13, 2, 1, 5, 'Excellent Python for the GTFS pipeline'],
  [2, 4, 11, 4, 'Designed the warehouse schema'],
  [4, 7, 6, 3, 'Solid React dashboard'],
  [7, 6, 1, 2, 'Learning fast'],
  [11, 4, 1, 4, 'Reliable backend developer'],
  [12, 2, 13, 4, 'Sharp data analysis'],
  [3, 7, 15, 4, 'Designed our graph model']
] AS e
MATCH (a:User {id: e[0]})-[:COLLABORATED_WITH]-(b:User {id: e[1]})
MERGE (a)-[x:ENDORSES {skill_id: e[2]}]->(b)
SET x.weight = e[3], x.note = e[4], x.at = datetime();
