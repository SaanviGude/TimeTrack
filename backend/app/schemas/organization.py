# Organization specific schemas
# backend/app/schemas/organization.py

import uuid
from typing import List
from pydantic import Field
from .base import BaseSchema, BaseDBSchema
from enum import IntEnum

# Enum for Organization Roles with integer values
class OrganizationRole(IntEnum):
    OWNER = 1
    MEMBER = 2

# --- Schemas for Organization Member ---
class OrganizationMemberRole(BaseSchema):
    role: OrganizationRole = Field(OrganizationRole.MEMBER, description="Role of the member in the organization")

class OrganizationMemberCreate(OrganizationMemberRole):
    user_id: uuid.UUID = Field(..., description="ID of the user to invite/add to the organization")

class OrganizationMemberUpdate(OrganizationMemberRole):
    role: OrganizationRole | None = Field(None, description="New role for the organization member")

# Response schema for Organization Member (includes user details)
class OrganizationMemberResponse(OrganizationMemberRole, BaseDBSchema):
    user_id: uuid.UUID
    organization_id: uuid.UUID
    user: 'UserResponse' # Forward reference to UserResponse for embedding user details

# --- Schemas for Organization ---
class OrganizationBase(BaseSchema):
    name: str = Field(..., min_length=1, description="Name of the organization")
    description: str | None = Field(None, description="Optional description of the organization")

class OrganizationCreate(OrganizationBase):
    # Owner will be the current authenticated user
    pass

class OrganizationUpdate(OrganizationBase):
    name: str | None = None
    description: str | None = None

class OrganizationResponse(OrganizationBase, BaseDBSchema):
    owner_id: uuid.UUID # ID of the user who owns the organization
    members: List[OrganizationMemberResponse] = Field([], description="List of members in this organization")
    # workspaces: List['WorkspaceResponse'] = Field([], description="List of workspaces within this organization") # Optional: embed workspaces directly

# Rebuild forward references
OrganizationMemberResponse.model_rebuild()