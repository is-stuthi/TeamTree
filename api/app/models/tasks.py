from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["To Do", "In Progress", "Done", "Blocked"]
Priority = Literal["Low", "Medium", "High", "Critical"]


class TaskCreate(BaseModel):
    t_name: str = Field(min_length=1, max_length=150, title="Task")
    description: str | None = Field(default=None, max_length=2000, title="Description")
    priority: Priority = Field(default="Medium", title="Priority")
    due_date: date | None = Field(default=None, title="Due date")
    u_id: int | None = Field(default=None, title="Assignee")
    parent_task_id: int | None = Field(default=None, title="Parent task")


class TaskPatch(BaseModel):
    """Only columns tt_app may UPDATE on Task (column-level GRANT)."""
    t_name: str | None = Field(default=None, min_length=1, max_length=150, title="Task")
    description: str | None = Field(default=None, max_length=2000, title="Description")
    status: TaskStatus | None = Field(default=None, title="Status")
    priority: Priority | None = Field(default=None, title="Priority")
    due_date: date | None = Field(default=None, title="Due date")


class AssignIn(BaseModel):
    u_id: int | None = Field(default=None, title="Assignee")


class TaskOut(BaseModel):
    task_id: int
    p_id: int
    u_id: int | None = None
    assignee_name: str | None = None
    parent_task_id: int | None = None
    t_name: str
    description: str | None = None
    status: TaskStatus
    priority: Priority
    due_date: date | None = None
    is_overdue: bool


class TaskNode(TaskOut):
    depth: int
    path: str


class MyTask(TaskOut):
    p_name: str
