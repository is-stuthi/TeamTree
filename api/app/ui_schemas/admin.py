from app.models.skills import SkillCreate
from app.ui_schemas.base import spec

spec("skill_admin", "Add skill to catalogue", SkillCreate, "POST", "/admin/skills",
     fields={"category": {"placeholder": "e.g. Programming, Web, Data"}},
     submit_label="Add skill", success_message="Skill added")
