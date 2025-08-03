# Models package
# backend/app/models/__init__.py

# Import Base first to ensure it's available for other models to inherit from
from .base import BaseModel # Base is needed for Alembic to discover tables

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .organization import Organization, OrganizationMember
from .workspace import Workspace, WorkspaceMember
from .project import Project, ProjectMember
from .task import Task
from .time_entry import TimeEntry

__all__ = [
    "BaseModel",
    "User",
    "Organization",
    "OrganizationMember", 
    "Workspace",
    "WorkspaceMember",
    "Project",
    "ProjectMember",
    "Task",
    "TimeEntry",
]