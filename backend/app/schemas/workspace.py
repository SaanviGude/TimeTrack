# Workspace specific schemas
# backend/app/schemas/workspace.py

import uuid
from typing import List
from pydantic import Field
from .base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Workspace Roles with integer values
class WorkspaceRole(IntEnum):
    ADMIN = 1
    MEMBER = 2

# --- Schemas for Workspace Member ---
class WorkspaceMemberRole(BaseSchema):
    role: WorkspaceRole = Field(WorkspaceRole.MEMBER, description="Role of the member in the workspace")

class WorkspaceMemberCreate(WorkspaceMemberRole):
    user_id: uuid.UUID = Field(..., description="ID of the user to add to the workspace")

class WorkspaceMemberUpdate(WorkspaceMemberRole):
    role: WorkspaceRole | None = Field(None, description="New role for the workspace member")

# Response schema for Workspace Member (includes user details)
class WorkspaceMemberResponse(WorkspaceMemberRole, BaseDBSchema):
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    user: 'UserResponse' # Forward reference to UserResponse for embedding user details

# --- Schemas for Workspace ---
class WorkspaceBase(BaseSchema):
    name: str = Field(..., min_length=1, description="Name of the workspace")
    description: str | None = Field(None, description="Description of the workspace")

class WorkspaceCreate(WorkspaceBase):
    # When a user creates a workspace, they become the owner
    pass

class WorkspaceUpdate(WorkspaceBase):
    name: str | None = None
    description: str | None = None

class WorkspaceResponse(WorkspaceBase, BaseDBSchema):
    owner_id: uuid.UUID        # The user who owns this workspace
    members: List[WorkspaceMemberResponse] = Field([], description="List of members in this workspace")
    # projects: List['ProjectResponse'] = Field([], description="List of projects within this workspace") # Optional: embed projects

# Rebuild forward references
WorkspaceMemberResponse.model_rebuild()