"""Passwords (bcrypt), JWT sessions and the FastAPI auth dependencies.

App roles: 'admin' and 'member' (Users.role). Contextual roles (owner, team
member) are checked inside the stored procedures via the actor argument.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import db
from app.errors import ApiError
from app.settings import get_settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str
    email: str
    name: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def create_token(user_id: int, role: str, name: str) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    claims = {"sub": str(user_id), "role": role, "name": name,
              "iat": now, "exp": now + timedelta(minutes=s.jwt_ttl_minutes)}
    return jwt.encode(claims, s.jwt_secret, algorithm="HS256")


def _decode(token: str) -> int:
    try:
        return int(jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as e:
        raise ApiError(401, "INVALID_TOKEN") from e


async def current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> CurrentUser:
    """Valid JWT *and* a still-active account (role is re-read, so changes apply immediately)."""
    if creds is None:
        raise ApiError(401, "NOT_AUTHENTICATED")
    row = await db.fetch_one(
        "SELECT id, role, email, CONCAT(f_name, ' ', l_name) AS name, is_active FROM Users WHERE id = %s",
        (_decode(creds.credentials),),
    )
    if row is None or not row["is_active"]:
        raise ApiError(401, "USER_INACTIVE")
    return CurrentUser(row["id"], row["role"], row["email"], row["name"])


async def optional_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> CurrentUser | None:
    """For public endpoints that show extra context to logged-in viewers."""
    if creds is None:
        return None
    try:
        return await current_user(creds)
    except ApiError:
        return None


def require_role(role: str):
    async def checker(user: CurrentUser = Depends(current_user)) -> CurrentUser:
        if user.role != role:
            raise ApiError(403, "FORBIDDEN_ROLE", f"Requires role '{role}'")
        return user
    return checker


require_admin = require_role("admin")
