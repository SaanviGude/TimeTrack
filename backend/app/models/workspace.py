# Workspace and WorkspaceMember models
# backend/app/models/workspace.py

from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

# Define the enum locally to avoid circular imports


class WorkspaceRole(IntEnum):
    ADMIN = 1
    MEMBER = 2


class Workspace(BaseModel):
    __tablename__ = "workspaces"

    name = Column(String, index=True, nullable=False,
                  comment="Name of the workspace")
    description = Column(String, nullable=True,
                         comment="Description of the workspace")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                      comment="ID of the user who owns this workspace")

    # Relationships
    owner = relationship("User", back_populates="owned_workspaces")
    members = relationship(
        "WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship(
        "Project", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(BaseModel):
    __tablename__ = "workspace_members"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False,
                          comment="ID of the workspace")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                     comment="ID of the user who is a member")
    role = Column(Enum(WorkspaceRole, name='workspace_role_enum'), default=WorkspaceRole.MEMBER, nullable=False,
                  comment="Role of the user within the workspace")

    # Soft delete fields
    is_deleted = Column(Boolean, default=False,
                        nullable=False, comment="Soft delete flag")
    deleted_at = Column(DateTime, nullable=True,
                        comment="Timestamp when the member was deleted")

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")
