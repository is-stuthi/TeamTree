from pydantic import BaseModel, Field

from app.models.graph import EndorseIn, RelationIn
from app.ui_schemas.base import spec


class SemanticSearch(BaseModel):
    q: str = Field(min_length=2, max_length=200, title="Describe what you want to work on")


spec("graph_search", "Semantic project search", SemanticSearch, "GET", "/graph/search/projects",
     fields={"q": {"placeholder": "e.g. machine learning for farmers, or a security lab for students",
                   "help": "Matched by meaning (vector embeddings), not keywords"}},
     submit_label="Search", success_message="")

# `to` is a hidden field prefilled with the profile being viewed; skills come from that user.
spec("endorse", "Endorse a skill", EndorseIn, "PUT", "/graph/endorsements",
     order=["to", "skill_id", "weight", "note"],
     fields={"to": {"hidden": True},
             "skill_id": {"widget": "remote-select", "source": "/users/{to}/skills",
                          "label_key": "s_name", "value_key": "s_id", "placeholder": "Choose one of their skills"},
             "weight": {"help": "1 = some experience together, 5 = outstanding"},
             "note": {"placeholder": "Optional: what they did"}},
     submit_label="Endorse", success_message="Endorsement saved")

_SKILL = {"widget": "remote-select", "source": "/skills", "label_key": "s_name", "value_key": "s_id"}
spec("relation_add", "Relate two skills", RelationIn, "POST", "/graph/skill-relations",
     fields={"a": {**_SKILL, "placeholder": "Skill"}, "b": {**_SKILL, "placeholder": "Related skill"},
             "weight": {"help": "0 = loosely related, 1 = nearly interchangeable"}},
     submit_label="Save relation", success_message="Relation saved")
