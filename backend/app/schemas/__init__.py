# Imports all for easy access and forward reference resolution
# backend/app/schemas/__init__.py

# Import all base schemas first
from .time_entry import TimeEntryBase, TimeEntryCreate, TimeEntryStop, TimeEntryUpdate, TimeEntryResponse
from .task import TaskStatus, TaskBase, TaskCreate, TaskUpdate, TaskResponse
from .base import BaseSchema, BaseDBSchema, IDSchema, TimeStampSchema

# Import auth and user schemas first (needed by other schemas)
from .auth import UserSignup, UserLogin, Token, TokenPayload
from .user import UserBase, UserResponse, UserUpdate

# Import other schemas (these may reference UserResponse)
from .workspace import (
    WorkspaceRole, WorkspaceBase, WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse,
    WorkspaceMemberRole, WorkspaceMemberCreate, WorkspaceMemberUpdate, WorkspaceMemberResponse
)

from .project import (
    ProjectStatus, ProjectRole, ProjectBase, ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMemberRole, ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
)

from .task import (
    TaskStatus, TaskBase, TaskCreate, TaskUpdate, TaskResponse
)

from .time_entry import (
    TimeEntryBase, TimeEntryCreate, TimeEntryUpdate, TimeEntryResponse
)

# Rebuild forward references after all imports
WorkspaceMemberResponse.model_rebuild()
ProjectMemberResponse.model_rebuild()
TaskResponse.model_rebuild()
TimeEntryResponse.model_rebuild()

# Task schemas

# Time Entry schemas
