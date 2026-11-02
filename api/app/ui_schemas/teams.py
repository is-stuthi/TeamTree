from app.models.tasks import TaskCreate, TaskPatch
from app.models.teams import TransferIn
from app.ui_schemas.base import spec

# {p_id} in a remote-select source is filled from the form's params.
_MEMBER = {"widget": "remote-select", "source": "/projects/{p_id}/team",
           "label_key": "member_name", "value_key": "u_id"}

spec("task_create", "New task", TaskCreate, "POST", "/projects/{p_id}/tasks",
     order=["t_name", "description", "priority", "due_date", "u_id", "parent_task_id"],
     fields={"description": {"widget": "textarea", "rows": 3},
             "u_id": {**_MEMBER, "placeholder": "Unassigned", "help": "Only active team members"},
             "parent_task_id": {"widget": "remote-select", "source": "/projects/{p_id}/tasks",
                                "label_key": "t_name", "value_key": "task_id",
                                "placeholder": "None (top-level task)"},
             "due_date": {"help": "Must not be after the project deadline"}},
     submit_label="Create task", success_message="Task created")

spec("task_edit", "Edit task", TaskPatch, "PATCH", "/tasks/{task_id}",
     order=["t_name", "description", "status", "priority", "due_date"],
     fields={"description": {"widget": "textarea", "rows": 3}},
     submit_label="Save task", success_message="Task updated")

spec("transfer_ownership", "Transfer ownership", TransferIn, "POST", "/projects/{p_id}/transfer",
     fields={"new_owner": {**_MEMBER, "placeholder": "Choose a team member",
                           "help": "You stay on the team as a member. This is recorded in the audit table."}},
     submit_label="Transfer", success_message="Ownership transferred")
