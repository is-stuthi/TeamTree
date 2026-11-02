"""Text embeddings for the Neo4j vector indexes (384-dim, cosine).

Model: sentence-transformers/all-MiniLM-L6-v2 (free, local, CPU). Loaded once,
lazily, and run in a worker thread so encoding never blocks the event loop.
"""
import asyncio
import threading
from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIMS = 384
_lock = threading.Lock()


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer   # heavy import: only when first needed
    return SentenceTransformer(MODEL_NAME)


def _encode(texts: list[str]) -> list[list[float]]:
    with _lock:
        vectors = _model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [[float(x) for x in v] for v in vectors]


async def embed(texts: list[str]) -> list[list[float]]:
    return await asyncio.to_thread(_encode, texts)


async def embed_one(text: str) -> list[float]:
    return (await embed([text]))[0]


def project_text(p: dict) -> str:
    """name + description + domains + required skills."""
    parts = [p.get("p_name") or "", p.get("description") or "",
             "Domains: " + ", ".join(p.get("domains") or []),
             "Skills needed: " + ", ".join(p.get("skills") or [])]
    return ". ".join(x for x in parts if x.strip(" .:"))


def user_text(u: dict) -> str:
    """bio + skills with levels."""
    skills = ", ".join(f"{s['s_name']} ({s['u_s_level']})" for s in u.get("skills") or [])
    return ". ".join(x for x in [u.get("bio") or "", f"Skills: {skills}" if skills else ""] if x)
