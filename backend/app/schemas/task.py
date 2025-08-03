# Task and Subtask specific schemas
# backend/app/schemas/task.py

import uuid
from datetime import datetime
from typing import List
from pydantic import Field
from backend.app.schemas.base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Task Status
class TaskStatus(IntEnum):
    OPEN = 1
    COMPLETED = 2

# --- Schemas for Task / Subtask ---
class TaskBase(BaseSchema):
    # 'name' for top-level tasks, 'description' for subtasks aligns with your input
    name: str | None = Field(None, description="Name of the task (for top-level tasks)")
    description: str | None = Field(None, description="Description of the task/subtask")
    assigned_to_id: uuid.UUID | None = Field(None, description="ID of the user assigned to this task/subtask")
    deadline: datetime | None = Field(None, description="Optional deadline for the task/subtask")
    status: TaskStatus = Field(TaskStatus.OPEN, description="Current status of the task/subtask")

class TaskCreate(TaskBase):
    project_id: uuid.UUID | None = Field(None, description="ID of the project this task belongs to (required for top-level tasks)")
    parent_task_id: uuid.UUID | None = Field(None, description="ID of the parent task (for subtasks)")

    # Validation logic to ensure either project_id OR parent_task_id is set
    # and not both, can be added using Pydantic's @model_validator or custom validators
    # For now, keeping it simple as per frontend input request.

class TaskUpdate(TaskBase):
    name: str | None = None
    description: str | None = None
    assigned_to_id: uuid.UUID | None = None
    deadline: datetime | None = None
    status: TaskStatus | None = None
    # project_id and parent_task_id typically not updated after creation

class TaskResponse(TaskBase, BaseDBSchema):
    project_id: uuid.UUID | None = None
    parent_task_id: uuid.UUID | None = None
    assigned_to: 'UserResponse' | None = Field(None, description="Assigned user's details")
    subtasks: List['TaskResponse'] = Field([], description="List of subtasks for this task")

# Rebuild forward references (crucial for recursive schemas like TaskResponse)
TaskResponse.model_rebuild()