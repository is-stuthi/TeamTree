from app.models.applications import AcceptForm, ApplicationCreate
from app.ui_schemas.base import spec

spec("application_create", "Apply to this project", ApplicationCreate, "POST", "/projects/{p_id}/applications",
     fields={"msg": {"widget": "textarea", "rows": 6,
                     "placeholder": "Your relevant skills, what you'd like to work on, availability…",
                     "help": "At least 20 characters. The owner reads this when reviewing."}},
     submit_label="Send application", success_message="Application sent")

spec("application_accept", "Accept applicant", AcceptForm, "POST", "/applications/{a_id}/decision",
     fields={"decision": {"hidden": True},
             "role": {"placeholder": "e.g. Frontend Developer (defaults to Member)"}},
     submit_label="Accept and add to team", success_message="Applicant added to the team")
