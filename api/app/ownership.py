"""Owner checks for endpoints that write tables tt_app may touch directly
(Project columns, Domain, Requires). Writes to Application/Joins/Team go
through procedures, which do this check inside the database."""
from app import db
from app.auth import CurrentUser
from app.errors import ApiError
from app.queries import projects as q


async def project_owner(p_id: int) -> int:
    row = await db.fetch_one(q.OWNER, (p_id,))
    if row is None:
        raise ApiError(404, "PROJECT_NOT_FOUND")
    return row["owner_id"]


async def require_owner(p_id: int, user: CurrentUser) -> None:
    if await project_owner(p_id) != user.id:
        raise ApiError(403, "NOT_OWNER", "Only the project owner can do that")
