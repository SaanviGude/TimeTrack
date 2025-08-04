# Task CRUD operations
from sqlalchemy.orm import Session
from .. import models
from ..schemas.task import TaskCreate, TaskUpdate, TaskStatus
import uuid
from datetime import datetime


def create_task(db: Session, task: TaskCreate):
    """Create new task or subtask"""
    db_task = models.Task(
        name=task.name,
        description=task.description,
        assigned_to_id=task.assigned_to_id,
        deadline=task.deadline,
        status=task.status,
        project_id=task.project_id,
        parent_task_id=task.parent_task_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_project_tasks(db: Session, project_id: uuid.UUID, include_subtasks: bool = True):
    """Get all top-level tasks for a project"""
    query = db.query(models.Task).filter(
        models.Task.project_id == project_id,
        models.Task.is_deleted == False
    )
    
    if not include_subtasks:
        query = query.filter(models.Task.parent_task_id.is_(None))
    
    return query.all()


def get_task_by_id(db: Session, task_id: uuid.UUID):
    """Get task with subtasks"""
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.is_deleted == False
    ).first()


def get_user_tasks(db: Session, user_id: uuid.UUID, status: TaskStatus = None):
    """Get all tasks assigned to user"""
    query = db.query(models.Task).filter(
        models.Task.assigned_to_id == user_id,
        models.Task.is_deleted == False
    )
    
    if status:
        query = query.filter(models.Task.status == status)
    
    return query.all()


def update_task(db: Session, task_id: uuid.UUID, task_update: TaskUpdate):
    """Update task details"""
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    
    return db_task


def get_task_subtasks(db: Session, parent_task_id: uuid.UUID):
    """Get all subtasks for a parent task"""
    return db.query(models.Task).filter(
        models.Task.parent_task_id == parent_task_id,
        models.Task.is_deleted == False
    ).all()


def create_subtask(db: Session, parent_task_id: uuid.UUID, subtask: TaskCreate):
    """Create subtask under a parent task"""
    # Override project_id and parent_task_id for subtask
    subtask.project_id = None  # Subtasks don't directly belong to projects
    subtask.parent_task_id = parent_task_id
    
    return create_task(db, subtask)


def update_task_status(db: Session, task_id: uuid.UUID, status: TaskStatus):
    """Update task status"""
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    
    if db_task:
        db_task.status = status
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    
    return db_task


def assign_task(db: Session, task_id: uuid.UUID, user_id: uuid.UUID):
    """Assign task to a user"""
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    
    if db_task:
        db_task.assigned_to_id = user_id
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    
    return db_task


def unassign_task(db: Session, task_id: uuid.UUID):
    """Remove task assignment"""
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    
    if db_task:
        db_task.assigned_to_id = None
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    
    return db_task


def soft_delete_task(db: Session, task_id: uuid.UUID):
    """Soft delete task and all its subtasks"""
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    
    if db_task:
        # Delete subtasks first
        subtasks = get_task_subtasks(db, task_id)
        for subtask in subtasks:
            subtask.is_deleted = True
            subtask.updated_at = datetime.utcnow()
        
        # Delete main task
        db_task.is_deleted = True
        db_task.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False
