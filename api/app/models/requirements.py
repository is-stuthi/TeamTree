from pydantic import BaseModel, Field

from app.models.common import Level


class RequirementIn(BaseModel):
    s_id: int = Field(title="Skill")
    req_role: str = Field(default="Contributor", min_length=1, max_length=100, title="Role")
    p_s_level: Level = Field(title="Minimum level")
    req_count: int = Field(default=1, ge=1, le=20, title="People needed")


class RequirementOut(BaseModel):
    s_id: int
    s_name: str
    category: str | None = None
    req_role: str
    p_s_level: Level
    req_count: int


class RequirementCopy(BaseModel):
    src_p_id: int = Field(title="Copy from project")
