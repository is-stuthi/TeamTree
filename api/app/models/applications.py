from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.common import Availability, Level

AppStatus = Literal["Pending", "Accepted", "Rejected", "Withdrawn"]


class ApplicationCreate(BaseModel):
    msg: str = Field(min_length=20, max_length=2000, title="Why do you want to join?")


class Decision(BaseModel):
    decision: Literal["Accepted", "Rejected"] = Field(title="Decision")
    role: str | None = Field(default=None, max_length=100, title="Role in the team")


class AcceptForm(BaseModel):
    """Form-friendly accept: decision is a hidden constant, the owner only types a role."""
    decision: Literal["Accepted"] = Field(default="Accepted", title="Decision")
    role: str | None = Field(default=None, max_length=100, title="Role in the team")


class ApplicationOut(BaseModel):
    a_id: int
    p_id: int
    p_name: str
    project_status: str
    applicant_id: int
    applicant_name: str
    msg: str | None = None
    status: AppStatus
    a_date: datetime
    decision_date: datetime | None = None


class SkillBrief(BaseModel):
    s_name: str
    level: Level


class ReceivedApplication(ApplicationOut):
    experience_level: Level
    availability: Availability
    skills: list[SkillBrief] = []
    matched_requirements: int
    total_requirements: int
