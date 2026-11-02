"""Neo4j READ features (rubric 9): collaborator network, recommendations,
shortest path, related skills, gap candidates, and vector similarity search."""
from fastapi import APIRouter, Depends, Query

from app import db
from app.auth import CurrentUser, current_user
from app.graph.driver import run
from app.graph.embed import embed_one
from app.models.graph import (ConnectionPath, EndorsementSummary, GapCandidate, Network,
                              RecommendedCollaborator, RelatedSkills, SimilarItem, SkillRelation)
from app.ownership import require_owner
from app.queries import graph as q

router = APIRouter(prefix="/graph", tags=["graph"])


def degrees(me: int, edges: list[dict]) -> dict[int, int]:
    """BFS hop count from `me` over undirected collaboration edges."""
    adj: dict[int, set[int]] = {}
    for e in edges:
        adj.setdefault(e["source"], set()).add(e["target"])
        adj.setdefault(e["target"], set()).add(e["source"])
    seen, frontier = {me: 0}, [me]
    while frontier:
        nxt = []
        for n in frontier:
            for m in adj.get(n, ()):
                if m not in seen:
                    seen[m] = seen[n] + 1
                    nxt.append(m)
        frontier = nxt
    return seen


@router.get("/users/{uid}/network", response_model=Network)
async def network(uid: int, depth: int = Query(2, ge=1, le=2), _: CurrentUser = Depends(current_user)):
    edges = await run(q.NETWORK_EDGES, uid=uid, depth=depth)
    deg = degrees(uid, edges)
    names = {r["id"]: r["name"] for r in await run(q.NAMES, ids=list(deg))}
    nodes = [{"id": i, "name": names.get(i, "?"), "degree": d} for i, d in sorted(deg.items(), key=lambda x: x[1])]
    return {"nodes": nodes, "edges": edges}


@router.get("/users/{uid}/recommended-collaborators", response_model=list[RecommendedCollaborator])
async def recommended(uid: int, _: CurrentUser = Depends(current_user)):
    return await run(q.RECOMMENDED, uid=uid)


@router.get("/path", response_model=ConnectionPath)
async def path(src: int = Query(alias="from"), dst: int = Query(alias="to"), _: CurrentUser = Depends(current_user)):
    if src == dst:                                   # shortestPath rejects identical endpoints
        names = await run(q.NAMES, ids=[src])
        return {"path": names[:1], "hops": 0 if names else None}
    rows = await run(q.PATH, src=src, dst=dst)
    return rows[0] if rows else {"path": [], "hops": None}


@router.get("/skills/{sid}/related", response_model=RelatedSkills)
async def related(sid: int):
    rows = await run(q.RELATED, sid=sid)
    return rows[0] if rows else {"curated": [], "co_occurring": []}


@router.get("/skill-relations", response_model=list[SkillRelation])
async def relations():
    return await run(q.RELATIONS)


@router.get("/projects/{pid}/gap-candidates", response_model=list[GapCandidate])
async def gap_candidates(pid: int, user: CurrentUser = Depends(current_user)):
    await require_owner(pid, user)          # candidate search is an owner tool
    gaps = await db.fetch_all("SELECT DISTINCT s_id FROM SkillGap WHERE p_id = %s AND shortfall > 0", (pid,))
    if not gaps:
        return []
    return await run(q.GAP_CANDIDATES, skills=[g["s_id"] for g in gaps], pid=pid)


@router.get("/search/projects", response_model=list[SimilarItem])
async def search_projects(q_: str = Query(alias="q", min_length=2, max_length=200), limit: int = Query(8, ge=1, le=20)):
    return await run(q.SEARCH_PROJECTS, vec=await embed_one(q_), k=limit * 3, limit=limit)


@router.get("/projects/{pid}/similar", response_model=list[SimilarItem])
async def similar_projects(pid: int, limit: int = Query(4, ge=1, le=10)):
    return await run(q.SIMILAR_PROJECTS, id=pid, k=limit + 1, limit=limit)


@router.get("/users/{uid}/similar", response_model=list[SimilarItem])
async def similar_users(uid: int, limit: int = Query(5, ge=1, le=10), _: CurrentUser = Depends(current_user)):
    return await run(q.SIMILAR_USERS, id=uid, k=limit + 1, limit=limit)


@router.get("/users/{uid}/endorsements", response_model=list[EndorsementSummary])
async def endorsements(uid: int, _: CurrentUser = Depends(current_user)):
    return await run(q.ENDORSEMENTS, id=uid)
