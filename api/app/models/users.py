from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.common import AppRole, Availability, Level


class UserMe(BaseModel):
    id: int
    f_name: str
    m_name: str | None = None
    l_name: str
    email: str
    role: AppRole
    bio: str | None = None
    location: str | None = None
    dob: date | None = None
    experience_level: Level
    availability: Availability
    created_at: datetime


class UserPublic(BaseModel):
    id: int
    name: str
    bio: str | None = None
    location: str | None = None
    experience_level: Level
    availability: Availability
    skills: list["UserSkillOut"] = []


class ProfilePatch(BaseModel):
    """Only columns tt_app holds UPDATE privilege on (see db/007_rbac.sql)."""
    f_name: str | None = Field(default=None, min_length=1, max_length=50, title="First name")
    m_name: str | None = Field(default=None, max_length=50, title="Middle name")
    l_name: str | None = Field(default=None, min_length=1, max_length=50, title="Last name")
    bio: str | None = Field(default=None, max_length=1000, title="Bio")
    location: str | None = Field(default=None, max_length=150, title="Location")
    dob: date | None = Field(default=None, title="Date of birth")
    experience_level: Level | None = Field(default=None, title="Experience level")
    availability: Availability | None = Field(default=None, title="Availability")


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, title="Current password", json_schema_extra={"format": "password"})
    new_password: str = Field(min_length=8, max_length=128, title="New password", json_schema_extra={"format": "password"})


class UserSkillOut(BaseModel):
    s_id: int
    s_name: str
    category: str | None = None
    u_s_level: Level


class SkillLevelIn(BaseModel):
    s_id: int = Field(title="Skill")
    level: Level = Field(title="Proficiency")


class LevelIn(BaseModel):
    level: Level = Field(title="Proficiency")
