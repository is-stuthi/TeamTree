from pydantic import BaseModel

from app.models.common import Availability, Level


class Breakdown(BaseModel):
    coverage: float
    proficiency: float
    experience: float
    domain: float
    availability: float


class CandidateOut(BaseModel):
    u_id: int
    name: str
    experience_level: Level
    availability: Availability
    score: float
    breakdown: Breakdown
    missing_skills: list[str]
    fully_qualified: bool


class SkillGapRow(BaseModel):
    s_id: int
    s_name: str
    req_role: str
    required_level: Level
    req_count: int
    members_with_skill: int
    qualified_members: int
    shortfall: int
