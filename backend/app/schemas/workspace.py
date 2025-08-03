# Workspace specific schemas
# backend/app/schemas/workspace.py

import uuid
from typing import List
from pydantic import Field
from backend.app.schemas.base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Workspace Roles with integer values
class WorkspaceRole(IntEnum):
    OWNER = 1
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
    profile_picture_url: str | None = Field(None, description="URL to the selected profile picture for the workspace")
    # Description removed based on your current simplified input for workspace

class WorkspaceCreate(WorkspaceBase):
    # When a user signs up and creates a default workspace, this is used.
    # The organization_id will be derived from the user's default organization
    # or created implicitly if they don't have one.
    pass

class WorkspaceUpdate(WorkspaceBase):
    name: str | None = None
    profile_picture_url: str | None = None

class WorkspaceResponse(WorkspaceBase, BaseDBSchema):
    organization_id: uuid.UUID # The organization this workspace belongs to
    owner_id: uuid.UUID        # The user who created this workspace
    members: List[WorkspaceMemberResponse] = Field([], description="List of members in this workspace")
    # projects: List['ProjectResponse'] = Field([], description="List of projects within this workspace") # Optional: embed projects

# Rebuild forward references
WorkspaceMemberResponse.model_rebuild()