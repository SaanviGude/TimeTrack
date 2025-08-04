# Workspace specific schemas
# backend/app/schemas/workspace.py

import uuid
from typing import List, Optional
from pydantic import Field
from .base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Workspace Roles with integer values


class WorkspaceRole(IntEnum):
    ADMIN = 1
    MEMBER = 2

# --- Schemas for Workspace Member ---


class WorkspaceMemberRole(BaseSchema):
    role: WorkspaceRole = Field(
        WorkspaceRole.MEMBER, description="Role of the member in the workspace")


class WorkspaceMemberCreate(WorkspaceMemberRole):
    user_id: uuid.UUID = Field(...,
                               description="ID of the user to add to the workspace")


class WorkspaceMemberUpdate(WorkspaceMemberRole):
    role: Optional[WorkspaceRole] = Field(
        None, description="New role for the workspace member")

# Response schema for Workspace Member (includes user details)


class WorkspaceMemberResponse(WorkspaceMemberRole, BaseDBSchema):
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    user: 'UserResponse'  # Forward reference to UserResponse for embedding user details

# --- Schemas for Workspace ---


class WorkspaceBase(BaseSchema):
    name: str = Field(..., min_length=1, description="Name of the workspace")
    description: Optional[str] = Field(
        None, description="Description of the workspace")


class WorkspaceCreate(WorkspaceBase):
    # When a user creates a workspace, they become the owner
    pass


class WorkspaceUpdate(WorkspaceBase):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceResponse(WorkspaceBase, BaseDBSchema):
    owner_id: uuid.UUID        # The user who owns this workspace
    members: List[WorkspaceMemberResponse] = Field(
        [], description="List of members in this workspace")
    # projects: List['ProjectResponse'] = Field([], description="List of projects within this workspace") # Optional: embed projects

# Note: Forward references will be rebuilt in __init__.py after all imports
