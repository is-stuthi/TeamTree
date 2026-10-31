"""Registration and login. Registration goes through the register_user
procedure because tt_app has no INSERT privilege on Users."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, create_token, current_user, hash_password, verify_password
from app.errors import ApiError
from app.graph import sync
from app.models.auth import LoginIn, RegisterIn, TokenOut
from app.models.users import UserMe
from app.queries import auth as q
from app.queries import users as user_q

router = APIRouter(prefix="/auth", tags=["auth"])


async def _token_for(user_id: int) -> TokenOut:
    me = await db.fetch_one(user_q.ME, (user_id,))
    token = create_token(me["id"], me["role"], f"{me['f_name']} {me['l_name']}")
    return TokenOut(access_token=token, user=UserMe(**me))


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(body: RegisterIn):
    (user_id,) = await db.call_proc("register_user", body.f_name, body.m_name, body.l_name,
                                    body.email, hash_password(body.password), out=1)
    await sync.upsert_user(user_id)
    return await _token_for(user_id)


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn):
    row = await db.fetch_one(q.CREDENTIALS, (body.email,))
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise ApiError(401, "INVALID_CREDENTIALS", "Wrong email or password")
    if not row["is_active"]:
        raise ApiError(403, "USER_INACTIVE", "This account has been deactivated")
    return await _token_for(row["id"])


@router.get("/me", response_model=UserMe)
async def me(user: CurrentUser = Depends(current_user)):
    return await db.fetch_one(user_q.ME, (user.id,))
