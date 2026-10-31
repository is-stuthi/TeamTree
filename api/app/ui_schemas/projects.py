from app.models.projects import ProjectCreate, ProjectFilter, ProjectPatch
from app.models.requirements import RequirementCopy, RequirementIn
from app.ui_schemas.base import spec

_SKILL = {"widget": "remote-select", "source": "/skills", "label_key": "s_name",
          "value_key": "s_id", "placeholder": "Choose a skill"}

spec("project_create", "New project", ProjectCreate, "POST", "/projects",
     fields={"description": {"widget": "textarea", "rows": 5},
             "domains": {"placeholder": "e.g. Web, Education (press Enter)"},
             "max_team_size": {"help": "Includes you (the owner). Leave empty for no limit."}},
     submit_label="Create project", success_message="Project created")

spec("project_edit", "Project settings", ProjectPatch, "PATCH", "/projects/{p_id}",
     order=["p_name", "description", "domains", "status", "deadline", "max_team_size"],
     fields={"description": {"widget": "textarea", "rows": 5},
             "status": {"help": "Open: recruiting · Ongoing: work started · Completed · Closed: archived "
                                "(closing blocks unfinished tasks; finished projects cannot reopen)"},
             "max_team_size": {"help": "Includes the owner"}})

spec("project_filter", "Find projects", ProjectFilter, "GET", "/projects",
     fields={"q": {"placeholder": "Name or description"},
             "domain": {"placeholder": "e.g. Web"},
             "skill": {**_SKILL, "placeholder": "Any skill"},
             "status": {"placeholder": "Any status"}},
     submit_label="Search", success_message="")

spec("requirement_add", "Add a requirement", RequirementIn, "PUT", "/projects/{p_id}/requirements",
     order=["s_id", "p_s_level", "req_role", "req_count"],
     fields={"s_id": _SKILL, "req_role": {"placeholder": "e.g. Backend Developer"}},
     submit_label="Save requirement", success_message="Requirement saved")

spec("requirement_copy", "Copy requirements", RequirementCopy, "POST", "/projects/{p_id}/requirements/copy",
     fields={"src_p_id": {"widget": "remote-select", "source": "/projects", "label_key": "p_name",
                          "value_key": "p_id", "placeholder": "Choose a project"}},
     submit_label="Copy", success_message="Requirements copied")
