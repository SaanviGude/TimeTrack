# backend/app/models/workspace.py

from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

# Define the enum locally to avoid circular imports
class WorkspaceRole(IntEnum):
    ADMIN = 1
    MEMBER = 2

class Workspace(BaseModel):
    __tablename__ = "workspaces"

    name = Column(String, index=True, nullable=False, comment="Name of the workspace")
    profile_picture_url = Column(String, nullable=True, comment="URL to the workspace's profile picture")
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False,
                             comment="ID of the organization this workspace belongs to")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                      comment="ID of the user who created this workspace")

    # Relationships
    organization = relationship("Organization", back_populates="workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(BaseModel):
    __tablename__ = "workspace_members"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), primary_key=True,
                          comment="ID of the workspace")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True,
                     comment="ID of the user who is a member")
    role = Column(Enum(WorkspaceRole, name='workspace_role_enum'), default=WorkspaceRole.MEMBER, nullable=False,
                  comment="Role of the user within the workspace (e.g., Admin, Member)")

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")# Workspace and WorkspaceMember models
