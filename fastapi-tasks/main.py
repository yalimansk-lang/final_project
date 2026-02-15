from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="FastAPI Tasks",
    version="1.0.0",
    description="Task management API with JSON Lines storage. All endpoints are available in Swagger UI at `/docs`.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

DATA_FILE = Path(__file__).with_name("tasks.txt")


class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    completed: bool = False


class TaskCreate(TaskBase):
    """Request body for creating a task; id is assigned by the server."""
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    completed: Optional[bool] = None


class Task(TaskBase):
    """Full task with server-assigned id (response and storage)."""
    id: int


# Ensure all models are fully built for OpenAPI schema generation (avoids "not fully defined" when loaded via launcher)
TaskCreate.model_rebuild()
TaskUpdate.model_rebuild()
Task.model_rebuild()


def _load_tasks() -> List[Task]:
    """
    Load all tasks from the text file.
    The file uses JSON Lines format: one JSON object per line.
    """
    if not DATA_FILE.exists():
        return []

    tasks: List[Task] = []
    for line in DATA_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        tasks.append(Task(**data))
    return tasks


def _save_tasks(tasks: List[Task]) -> None:
    """
    Persist all tasks to the text file in JSON Lines format.
    Each line is one complete task as a JSON object.
    """
    lines = [json.dumps(task.model_dump()) for task in tasks]
    contents = "\n".join(lines)
    if contents:
        contents += "\n"
    DATA_FILE.write_text(contents, encoding="utf-8")


def _get_next_id(tasks: List[Task]) -> int:
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Returns a simple message confirming the API is running.",
)
def read_root():
    return {"message": "FastAPI Tasks is running"}


@app.get(
    "/tasks",
    response_model=List[Task],
    tags=["tasks"],
    summary="List all tasks",
    description="Return all tasks from storage. Available in Swagger UI.",
)
def list_tasks() -> List[Task]:
    return _load_tasks()


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["tasks"],
    summary="Get task by ID",
    description="Return a single task by its id. Returns 404 if not found.",
)
def get_task(task_id: int) -> Task:
    tasks = _load_tasks()
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
    )


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
    summary="Create a task",
    description="Create a new task. Only `title` is required; `description` and `completed` are optional. Id is assigned by the server.",
)
def create_task(payload: TaskCreate) -> Task:
    tasks = _load_tasks()
    new_task = Task(
        id=_get_next_id(tasks),
        title=payload.title,
        description=payload.description,
        completed=payload.completed,
    )
    tasks.append(new_task)
    _save_tasks(tasks)
    return new_task


@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["tasks"],
    summary="Replace a task",
    description="Fully replace an existing task by id. Returns 404 if not found.",
)
def replace_task(task_id: int, payload: TaskCreate) -> Task:
    tasks = _load_tasks()
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated = Task(
                id=task_id,
                title=payload.title,
                description=payload.description,
                completed=payload.completed,
            )
            tasks[index] = updated
            _save_tasks(tasks)
            return updated

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
    )


@app.patch(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["tasks"],
    summary="Update a task (partial)",
    description="Partially update a task by id. Only sent fields are updated. Returns 404 if not found.",
)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    tasks = _load_tasks()
    for index, task in enumerate(tasks):
        if task.id == task_id:
            update_data = payload.model_dump(exclude_unset=True)
            updated = task.model_copy(update=update_data)
            tasks[index] = updated
            _save_tasks(tasks)
            return updated

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
    summary="Delete a task",
    description="Delete a task by id. Returns 204 on success, 404 if not found.",
)
def delete_task(task_id: int) -> None:
    tasks = _load_tasks()
    remaining = [task for task in tasks if task.id != task_id]
    if len(remaining) == len(tasks):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    _save_tasks(remaining)

