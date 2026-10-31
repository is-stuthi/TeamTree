from app.models.auth import LoginIn, RegisterIn
from app.models.users import LevelIn, PasswordChange, ProfilePatch, SkillLevelIn
from app.ui_schemas.base import spec

spec("login", "Log in", LoginIn, "POST", "/auth/login",
     submit_label="Log in", success_message="Welcome back")

spec("register", "Create your account", RegisterIn, "POST", "/auth/register",
     fields={"m_name": {"placeholder": "Optional"}, "password": {"help": "At least 8 characters"}},
     submit_label="Create account", success_message="Account created")

spec("profile_edit", "Profile", ProfilePatch, "PATCH", "/users/me",
     fields={"bio": {"widget": "textarea", "rows": 4},
             "location": {"placeholder": "City"},
             "experience_level": {"help": "Your overall experience, not per skill"}})

spec("password_change", "Change password", PasswordChange, "PUT", "/users/me/password",
     submit_label="Update password", success_message="Password updated")

# Path placeholder {s_id} is taken from the s_id field; the body is LevelIn ({level}).
assert set(LevelIn.model_fields) <= set(SkillLevelIn.model_fields)
spec("skill_add", "Add a skill", SkillLevelIn, "PUT", "/users/me/skills/{s_id}",
     fields={"s_id": {"widget": "remote-select", "source": "/skills",
                      "label_key": "s_name", "value_key": "s_id", "placeholder": "Choose a skill"}},
     submit_label="Add skill", success_message="Skill saved")
