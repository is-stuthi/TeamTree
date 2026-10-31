"""Single place that turns database errors into HTTP responses.

Stored procedures and triggers raise SIGNAL SQLSTATE '45000' with a stable
UPPER_SNAKE code (MySQL errno 1644). Constraint and privilege errors are
mapped by errno. Every new SIGNAL code must be added to SIGNAL_STATUS.
"""
import re

import pymysql
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

SIGNAL_STATUS: dict[str, int] = {
    # 403 - not allowed
    "NOT_OWNER": 403, "NOT_ADMIN": 403, "NOT_APPLICANT": 403, "NOT_MEMBER": 403,
    "USER_INACTIVE": 403,
    # 404 - missing
    "APP_NOT_FOUND": 404, "PROJECT_NOT_FOUND": 404, "TASK_NOT_FOUND": 404,
    "USER_NOT_FOUND": 404, "SKILL_NOT_FOUND": 404,
    # 409 - state conflicts
    "PROJECT_NOT_OPEN": 409, "PROJECT_FULL": 409, "APP_NOT_PENDING": 409,
    "ASSIGNEE_NOT_MEMBER": 409, "TASK_AFTER_DEADLINE": 409, "PROJECT_NOT_ACCEPTING": 409,
    "PROJECT_REOPEN_FORBIDDEN": 409, "LAST_ADMIN": 409, "OWNER_CANNOT_LEAVE": 409,
    "NOT_ACTIVE_MEMBER": 409, "OWNS_ONGOING_PROJECTS": 409, "ALREADY_MEMBER": 409,
    # 422 - invalid input
    "SELF_APPLICATION": 422, "BAD_DECISION": 422, "BAD_ROLE": 422,
}

DUPLICATE_KEYS: dict[str, str] = {
    "uq_application_pending": "DUPLICATE_PENDING",
    "uq_users_email": "EMAIL_TAKEN",
    "uq_skill_name_norm": "SKILL_EXISTS",
    "uq_joins_active": "ALREADY_MEMBER",
    "uq_team_project": "TEAM_EXISTS",
    "PRIMARY": "ALREADY_EXISTS",
}

ERRNO_STATUS: dict[int, tuple[int, str]] = {
    1142: (403, "DB_PERMISSION_DENIED"),   # table-level privilege missing
    1143: (403, "DB_PERMISSION_DENIED"),   # column-level privilege missing
    1370: (403, "DB_PERMISSION_DENIED"),   # EXECUTE privilege missing
    3819: (422, "CHECK_VIOLATION"),
    1452: (422, "INVALID_REFERENCE"),
    1216: (422, "INVALID_REFERENCE"),     # same as 1452, reported to users without parent-table privileges
    1451: (409, "IN_USE"),
    1217: (409, "IN_USE"),
    1048: (422, "MISSING_VALUE"),
}


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str | None = None):
        self.status, self.code, self.message = status, code, message or code
        super().__init__(code)


def map_mysql_error(err: pymysql.err.MySQLError) -> ApiError | None:
    errno, msg = (err.args + (None, ""))[:2]
    msg = str(msg)
    if errno == 1644:
        return ApiError(SIGNAL_STATUS.get(msg, 400), msg)
    if errno == 1062:
        key = re.search(r"for key '(?:[\w]+\.)?([\w]+)'", msg)
        code = DUPLICATE_KEYS.get(key.group(1) if key else "", "DUPLICATE")
        return ApiError(409, code, msg)
    if errno in ERRNO_STATUS:
        status, code = ERRNO_STATUS[errno]
        return ApiError(status, code, msg)
    return None


def _body(e: ApiError) -> dict:
    return {"code": e.code, "message": e.message}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, e: ApiError):
        return JSONResponse(status_code=e.status, content=_body(e))

    @app.exception_handler(pymysql.err.MySQLError)
    async def _mysql_error(_: Request, e: pymysql.err.MySQLError):
        mapped = map_mysql_error(e)
        if mapped is None:
            raise e
        return JSONResponse(status_code=mapped.status, content=_body(mapped))
