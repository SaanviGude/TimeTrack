# Task (and Subtask recursion) model
# backend/app/models/task.py

from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

# Define the enum locally to avoid circular imports
class TaskStatus(IntEnum):
    OPEN = 1
    COMPLETED = 2

class Task(BaseModel):
    __tablename__ = "tasks"

    name = Column(String, nullable=True, comment="Name of the task (for top-level tasks)")
    description = Column(Text, nullable=True, comment="Description of the task or subtask")
    deadline = Column(DateTime(timezone=True), nullable=True, comment="Optional deadline for the task/subtask (UTC)")
    status = Column(Enum(TaskStatus, name='task_status_enum'), default=TaskStatus.OPEN, nullable=False,
                    comment="Current status of the task/subtask")
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True,
                        comment="ID of the project this task belongs to (null for subtasks if they only link to parent)")
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True,
                            comment="ID of the user assigned to this task/subtask")
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True, index=True,
                            comment="ID of the parent task, if this is a subtask")

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    # Self-referencing relationship for subtasks
    parent_task = relationship("Task", remote_side="Task.id", back_populates="subtasks", foreign_keys=[parent_task_id])
    subtasks = relationship("Task", back_populates="parent_task", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")

    # Constraint to ensure a task is either a project task OR a subtask, not both
    # This logic can be enforced at the application level during creation or via DB constraint (CHECK constraint)
    # For now, models allow flexibility, but CRUDS/services should enforce this.
    # Eg: @validates('project_id', 'parent_task_id')
    # def validate_parentage(self, key, value):
    #     if self.project_id is not None and self.parent_task_id is not None:
    #         raise ValueError("Task cannot have both project_id and parent_task_id set.")
    #     if self.project_id is None and self.parent_task_id is None:
    #         raise ValueError("Task must have either a project_id or a parent_task_id.")
    #     return value