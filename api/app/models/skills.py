from pydantic import BaseModel, Field


class SkillOut(BaseModel):
    s_id: int
    s_name: str
    category: str | None = None
    users_possessing: int = 0


class SkillCreate(BaseModel):
    s_name: str = Field(min_length=1, max_length=100, title="Skill name")
    category: str | None = Field(default=None, max_length=100, title="Category")


class SkillPatch(BaseModel):
    s_name: str | None = Field(default=None, min_length=1, max_length=100, title="Skill name")
    category: str | None = Field(default=None, max_length=100, title="Category")
