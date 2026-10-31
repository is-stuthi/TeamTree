import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.errors import install_error_handlers
from app.graph import driver as graph
from app.settings import get_settings
from app.routers import auth
from app.routers import users
from app.routers import skills
from app.routers import admin
from app.routers import ui_schemas
from app.routers import projects
from app.routers import requirements
from app.routers import discovery
from app.routers import applications
# plop: router imports

log = logging.getLogger("teamtree")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.init_pool()
    try:
        await graph.init_driver()
    except Exception as e:  # noqa: BLE001 - graph is optional for MySQL features
        log.warning("Neo4j unavailable at startup: %s", e)
    yield
    await graph.close_driver()
    await db.close_pool()


app = FastAPI(title="TeamTREE API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_error_handlers(app)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(skills.router)
app.include_router(admin.router)
app.include_router(ui_schemas.router)
app.include_router(projects.router)
app.include_router(requirements.router)
app.include_router(discovery.router)
app.include_router(applications.router)
# plop: include routers


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    mysql_ok, neo4j_ok = await db.ping(), await graph.ping()
    return {
        "status": "ok" if mysql_ok and neo4j_ok else "degraded",
        "mysql": "ok" if mysql_ok else "down",
        "neo4j": "ok" if neo4j_ok else "down",
    }
