# Timer specific schemas
# backend/app/schemas/time_entry.py

import uuid
from datetime import datetime, timezone
from pydantic import Field
from backend.app.schemas.base import BaseSchema, BaseDBSchema

class TimeEntryBase(BaseSchema):
    start_time: datetime = Field(..., description="Start timestamp of the time entry (UTC)")
    end_time: datetime | None = Field(None, description="End timestamp of the time entry (UTC), null if timer is active")
    duration_minutes: float | None = Field(None, description="Calculated duration in minutes, null if timer is active")
    description: str | None = Field(None, description="Optional description for this time entry")

class TimeEntryCreate(TimeEntryBase):
    # When starting a timer, end_time and duration_minutes are null
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Start time (defaults to now)")
    user_id: uuid.UUID = Field(..., description="ID of the user performing the time entry")
    project_id: uuid.UUID = Field(..., description="ID of the project")
    task_id: uuid.UUID = Field(..., description="ID of the task")
    subtask_id: uuid.UUID | None = Field(None, description="Optional ID of the subtask")

class TimeEntryStop(BaseSchema):
    end_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="End time (defaults to now)")
    duration_minutes: float = Field(..., description="Calculated duration in minutes")

# This is for updating description of an *existing* stopped entry
class TimeEntryUpdate(BaseSchema):
    description: str | None = None

class TimeEntryResponse(TimeEntryBase, BaseDBSchema):
    user_id: uuid.UUID
    project_id: uuid.UUID
    task_id: uuid.UUID
    subtask_id: uuid.UUID | None = None
    # Optionally embed related objects for richer response
    # user: 'UserResponse' # If you want to embed user details
    # project: 'ProjectResponse' # If you want to embed project details
    # task: 'TaskResponse' # If you want to embed task details
    # subtask: 'TaskResponse' # If you want to embed subtask details