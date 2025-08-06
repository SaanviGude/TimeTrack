# Task and Subtask specific schemas
# backend/app/schemas/task.py

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import Field, field_validator
from .base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Task Status


class TaskStatus(IntEnum):
    COMPLETED = 1
    OPEN = 2

# --- Schemas for Task / Subtask ---


class TaskBase(BaseSchema):
    # 'name' for top-level tasks, 'description' for subtasks aligns with your input
    name: Optional[str] = Field(
        None, description="Name of the task (for top-level tasks)")
    description: Optional[str] = Field(
        None, description="Description of the task/subtask")
    assigned_to_id: Optional[uuid.UUID] = Field(
        None, description="ID of the user assigned to this task/subtask")
    deadline: Optional[datetime] = Field(
        None, description="Optional deadline for the task/subtask")
    status: TaskStatus = Field(
        TaskStatus.OPEN, description="Current status of the task/subtask")

    @field_validator('assigned_to_id', mode='before')
    @classmethod
    def validate_assigned_to_id(cls, v):
        if v == "" or v is None:
            return None
        return v

    @field_validator('deadline', mode='before')
    @classmethod
    def validate_deadline(cls, v):
        if v == "" or v is None:
            return None
        return v


class TaskCreate(TaskBase):
    project_id: Optional[uuid.UUID] = Field(
        None, description="ID of the project this task belongs to (required for top-level tasks)")
    parent_task_id: Optional[uuid.UUID] = Field(
        None, description="ID of the parent task (for subtasks)")

    @field_validator('project_id', mode='before')
    @classmethod
    def validate_project_id(cls, v):
        if v == "" or v is None:
            return None
        return v

    @field_validator('parent_task_id', mode='before')
    @classmethod
    def validate_parent_task_id(cls, v):
        if v == "" or v is None:
            return None
        return v

    # Validation logic to ensure either project_id OR parent_task_id is set
    # and not both, can be added using Pydantic's @model_validator or custom validators
    # For now, keeping it simple as per frontend input request.


class TaskUpdate(TaskBase):
    name: Optional[str] = None
    description: Optional[str] = None
    assigned_to_id: Optional[uuid.UUID] = None
    deadline: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    # project_id and parent_task_id typically not updated after creation


class TaskResponse(TaskBase, BaseDBSchema):
    project_id: Optional[uuid.UUID] = None
    parent_task_id: Optional[uuid.UUID] = None
    assigned_to: Optional['UserResponse'] = Field(
        None, description="Assigned user's details")
    subtasks: List['TaskResponse'] = Field(
        [], description="List of subtasks for this task")

# Note: Forward references will be rebuilt in __init__.py after all imports