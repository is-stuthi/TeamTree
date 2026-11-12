from datetime import datetime

from pydantic import BaseModel, Field

from app.models.common import AppRole


class AdminUserOut(BaseModel):
    id: int
    name: str
    email: str
    role: AppRole
    is_active: bool
    created_at: datetime


class RoleChange(BaseModel):
    role: AppRole = Field(title="Role")


class DevResetOut(BaseModel):
    mysql: str
    graph: str
