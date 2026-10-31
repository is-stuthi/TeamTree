from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.requirements import RequirementOut

ProjectStatus = Literal["Open", "Ongoing", "Completed", "Closed"]


class ProjectCreate(BaseModel):
    p_name: str = Field(min_length=3, max_length=150, title="Project name")
    description: str | None = Field(default=None, max_length=5000, title="Description")
    domains: list[str] = Field(default=[], max_length=8, title="Domains")
    deadline: date | None = Field(default=None, title="Deadline")
    max_team_size: int | None = Field(default=None, ge=1, le=50, title="Max team size")


class ProjectPatch(BaseModel):
    """Only columns tt_app may UPDATE (column-level GRANT). owner_id changes via transfer."""
    p_name: str | None = Field(default=None, min_length=3, max_length=150, title="Project name")
    description: str | None = Field(default=None, max_length=5000, title="Description")
    domains: list[str] | None = Field(default=None, max_length=8, title="Domains")
    deadline: date | None = Field(default=None, title="Deadline")
    status: ProjectStatus | None = Field(default=None, title="Status")
    max_team_size: int | None = Field(default=None, ge=1, le=50, title="Max team size")


class ProjectFilter(BaseModel):
    q: str | None = Field(default=None, max_length=100, title="Search")
    domain: str | None = Field(default=None, max_length=100, title="Domain")
    skill: int | None = Field(default=None, title="Requires skill")
    status: ProjectStatus | None = Field(default=None, title="Status")
    deadline_before: date | None = Field(default=None, title="Deadline before")


class ProjectCard(BaseModel):
    p_id: int
    p_name: str
    description: str | None = None
    deadline: date | None = None
    status: ProjectStatus
    max_team_size: int | None = None
    owner_id: int
    owner_name: str
    domains: list[str] = []
    required_skills: list[str] = []
    team_size: int
    is_overdue: bool


class RecommendedProject(ProjectCard):
    matched_requirements: int
    total_requirements: int


class MyProject(ProjectCard):
    my_role: str
    is_owner: bool


class Viewer(BaseModel):
    is_owner: bool = False
    is_member: bool = False
    pending_application_id: int | None = None


class ProjectDetail(BaseModel):
    p_id: int
    p_name: str
    description: str | None = None
    deadline: date | None = None
    status: ProjectStatus
    max_team_size: int | None = None
    creation_date: datetime
    owner_id: int
    owner_name: str
    owner_bio: str | None = None
    team_name: str
    team_size: int
    domains: list[str] = []
    is_overdue: bool
    requirements: list[RequirementOut] = []
    viewer: Viewer = Viewer()
