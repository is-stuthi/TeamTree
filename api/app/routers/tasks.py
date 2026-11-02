"""Tasks: create/edit by team members, assignment (assign_task procedure),
subtask tree (Q8 recursive CTE). Triggers validate assignee, due date and parent."""
from fastapi import APIRouter, Depends

from app import db
from app.auth import CurrentUser, current_user
from app.errors import ApiError
from app.models.tasks import AssignIn, MyTask, TaskCreate, TaskNode, TaskOut, TaskPatch
from app.ownership import require_member
from app.queries import tasks as q

router = APIRouter(tags=["tasks"])


async def _project_of(task_id: int) -> int:
    row = await db.fetch_one(q.PROJECT_OF, (task_id,))
    if row is None:
        raise ApiError(404, "TASK_NOT_FOUND")
    return row["p_id"]


@router.get("/projects/{p_id}/tasks", response_model=list[TaskOut])
async def list_tasks(p_id: int, user: CurrentUser = Depends(current_user)):
    await require_member(p_id, user)
    return await db.fetch_all(q.LIST, (p_id,))


@router.get("/projects/{p_id}/tasks/tree", response_model=list[TaskNode])
async def task_tree(p_id: int, user: CurrentUser = Depends(current_user)):
    await require_member(p_id, user)
    return await db.fetch_all(q.TREE, (p_id,))


@router.post("/projects/{p_id}/tasks", response_model=TaskOut, status_code=201)
async def create_task(p_id: int, body: TaskCreate, user: CurrentUser = Depends(current_user)):
    await require_member(p_id, user)
    async with db.cursor() as cur:
        await cur.execute(q.INSERT, (p_id, body.u_id, body.parent_task_id, body.t_name.strip(),
                                     body.description, body.priority, body.due_date))
        task_id = cur.lastrowid
    return await db.fetch_one(q.ONE, (task_id,))


@router.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, body: TaskPatch, user: CurrentUser = Depends(current_user)):
    await require_member(await _project_of(task_id), user)
    changes = {k: v for k, v in body.model_dump(exclude_unset=True).items()
               if v is not None or k not in q.NOT_NULL_COLUMNS}
    if changes:
        await db.execute(q.patch(list(changes)), (*changes.values(), task_id))
    return await db.fetch_one(q.ONE, (task_id,))


@router.post("/tasks/{task_id}/assign", response_model=TaskOut)
async def assign(task_id: int, body: AssignIn, user: CurrentUser = Depends(current_user)):
    await db.call_proc("assign_task", task_id, user.id, body.u_id)   # actor must be a member
    return await db.fetch_one(q.ONE, (task_id,))


@router.get("/users/me/tasks", response_model=list[MyTask])
async def my_tasks(user: CurrentUser = Depends(current_user)):
    return await db.fetch_all(q.MINE, (user.id,))
