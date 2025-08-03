# For tracking time model
# backend/app/models/time_entry.py

from sqlalchemy import Column, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class TimeEntry(BaseModel):
    __tablename__ = "time_entries"

    start_time = Column(DateTime(timezone=True), nullable=False,
                        comment="Timestamp when the time entry started (UTC)")
    end_time = Column(DateTime(timezone=True), nullable=True,
                      comment="Timestamp when the time entry ended (UTC), null if still running")
    duration_minutes = Column(Float, nullable=True,
                             comment="Calculated duration in minutes. Null if timer is still active. Automatically calculated on stop.")
    description = Column(Text, nullable=True,
                         comment="Optional description for this time entry")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                     comment="ID of the user who recorded this time entry")
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False,
                        comment="ID of the project linked to this time entry")
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False,
                     comment="ID of the task/subtask this time entry is for")

    # Relationships
    user = relationship("User")
    project = relationship("Project")
    task = relationship("Task", back_populates="time_entries")