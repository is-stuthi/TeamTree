from datetime import date

from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    j_id: int
    u_id: int
    member_name: str
    email: str
    role: str
    join_date: date
    leave_date: date | None = None
    is_active: bool
    open_tasks: int = 0


class TransferIn(BaseModel):
    new_owner: int = Field(title="New owner")


class MyTeam(BaseModel):
    p_id: int
    p_name: str
    team_name: str
    status: str
    role: str
    join_date: date
    is_owner: bool
    team_size: int


class TopContributor(BaseModel):
    u_id: int
    member_name: str
    done: int
