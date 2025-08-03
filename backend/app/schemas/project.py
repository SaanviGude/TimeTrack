# Project specific schemas
# backend/app/schemas/project.py

import uuid
from datetime import datetime
from typing import List
from pydantic import Field
from backend.app.schemas.base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Project Roles with integer values
class ProjectRole(IntEnum):
    MANAGER = 1
    MEMBER = 2

# Enum for Project Status (useful for filtering/tracking progress)
class ProjectStatus(IntEnum):
    ACTIVE = 1
    COMPLETED = 2

# --- Schemas for Project Member (Team) ---
class ProjectMemberRole(BaseSchema):
    role: ProjectRole = Field(ProjectRole.MEMBER, description="Role of the member in the project team")

class ProjectMemberCreate(ProjectMemberRole):
    user_id: uuid.UUID = Field(..., description="ID of the user to add to the project team")

class ProjectMemberUpdate(ProjectMemberRole):
    role: ProjectRole | None = Field(None, description="New role for the project member")

# Response schema for Project Member (includes user details)
class ProjectMemberResponse(ProjectMemberRole, BaseDBSchema):
    user_id: uuid.UUID
    project_id: uuid.UUID
    user: 'UserResponse' # Forward reference to UserResponse for embedding user details

# --- Schemas for Project ---
class ProjectBase(BaseSchema):
    name: str = Field(..., min_length=1, description="Name of the project")
    description: str | None = Field(None, description="Optional description of the project")
    deadline: datetime | None = Field(None, description="Optional project deadline")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Current status of the project")

class ProjectCreate(ProjectBase):
    workspace_id: uuid.UUID = Field(..., description="ID of the workspace this project belongs to")
    # Creator ID is derived from authenticated user context

class ProjectUpdate(ProjectBase):
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    status: ProjectStatus | None = None

class ProjectResponse(ProjectBase, BaseDBSchema):
    workspace_id: uuid.UUID
    creator_id: uuid.UUID
    members: List[ProjectMemberResponse] = Field([], description="List of members in this project team")
    # tasks: List['TaskResponse'] = Field([], description="List of tasks in this project") # Optional: embed tasks directly

# Rebuild forward references
ProjectMemberResponse.model_rebuild()