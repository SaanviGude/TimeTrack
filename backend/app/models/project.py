# Project and ProjectMember models
# backend/app/models/project.py

from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

# Define the enums locally to avoid circular imports


class ProjectStatus(IntEnum):
    COMPLETED = 1
    ACTIVE = 2


class ProjectRole(IntEnum):
    MANAGER = 1
    MEMBER = 2


class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(String, index=True, nullable=False,
                  comment="Name of the project")
    description = Column(Text, nullable=True,
                         comment="Description of the project")
    deadline = Column(DateTime(timezone=True), nullable=True,
                      comment="Optional project deadline (UTC)")
    status = Column(Enum(ProjectStatus, name='project_status_enum'), default=ProjectStatus.ACTIVE, nullable=False,
                    comment="Current status of the project")
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False,
                          comment="ID of the workspace this project belongs to")
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                        comment="ID of the user who created this project")

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    tasks = relationship("Task", back_populates="project",
                         cascade="all, delete-orphan")
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(BaseModel):
    __tablename__ = "project_members"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True,
                        comment="ID of the project")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True,
                     comment="ID of the user who is a member")
    role = Column(Enum(ProjectRole, name='project_role_enum'), default=ProjectRole.MEMBER, nullable=False,
                  comment="Role of the user within the project (e.g., Manager, Member)")
    
    # Soft delete fields
    is_deleted = Column(Boolean, default=False, nullable=False, comment="Soft delete flag")
    deleted_at = Column(DateTime, nullable=True, comment="Timestamp when the member was deleted")

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
