from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: int
    name: str
    degree: int              # 0 = me, 1 = collaborator, 2 = collaborator of a collaborator


class GraphEdge(BaseModel):
    source: int
    target: int
    shared: int


class Network(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class RecommendedCollaborator(BaseModel):
    id: int
    name: str
    mutual: int
    complementary_skills: list[str]
    endorsement_score: float


class PathNode(BaseModel):
    id: int
    name: str


class ConnectionPath(BaseModel):
    path: list[PathNode]
    hops: int | None


class RelatedSkill(BaseModel):
    id: int
    name: str
    weight: float | None = None
    together: int | None = None


class RelatedSkills(BaseModel):
    curated: list[RelatedSkill]
    co_occurring: list[RelatedSkill]


class SimilarItem(BaseModel):
    id: int
    name: str
    score: float


class GapCandidate(BaseModel):
    skill: str
    user_id: int
    name: str
    via: str                 # the skill they actually have (the gap skill or a related one)
    related: bool
    endorsements: float


class EndorsementSummary(BaseModel):
    skill_id: int
    skill: str
    count: int
    avg_weight: float
    endorsers: list[str]
    endorser_ids: list[int]


class SkillRelation(BaseModel):
    a: int
    a_name: str
    b: int
    b_name: str
    weight: float


class EndorseIn(BaseModel):
    to: int = Field(title="Endorse")
    skill_id: int = Field(title="Skill")
    weight: int = Field(ge=1, le=5, title="Strength (1-5)")
    note: str | None = Field(default=None, max_length=200, title="Note")


class WeightIn(BaseModel):
    weight: float = Field(ge=0, le=1, title="Relation strength (0-1)")


class RelationIn(BaseModel):
    a: int = Field(title="Skill")
    b: int = Field(title="Related skill")
    weight: float = Field(ge=0, le=1, title="Strength (0-1)")
