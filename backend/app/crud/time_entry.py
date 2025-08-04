# Time Entry CRUD operations
from sqlalchemy.orm import Session
from .. import models
from ..schemas.time_entry import TimeEntryCreate, TimeEntryStop, TimeEntryUpdate
import uuid
from datetime import datetime, timezone


def start_time_entry(db: Session, time_entry: TimeEntryCreate):
    """Start a new time entry (timer)"""
    db_time_entry = models.TimeEntry(
        start_time=time_entry.start_time,
        user_id=time_entry.user_id,
        project_id=time_entry.project_id,
        task_id=time_entry.task_id,
        description=time_entry.description
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def stop_time_entry(db: Session, time_entry_id: uuid.UUID, stop_data: TimeEntryStop):
    """Stop an active time entry"""
    db_time_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.id == time_entry_id,
        models.TimeEntry.end_time.is_(None)  # Only stop active timers
    ).first()
    
    if db_time_entry:
        db_time_entry.end_time = stop_data.end_time
        db_time_entry.duration_minutes = stop_data.duration_minutes
        db_time_entry.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_time_entry)
    
    return db_time_entry


def get_user_time_entries(db: Session, user_id: uuid.UUID, active_only: bool = False):
    """Get time entries for a user"""
    query = db.query(models.TimeEntry).filter(
        models.TimeEntry.user_id == user_id,
        models.TimeEntry.is_deleted == False
    )
    
    if active_only:
        query = query.filter(models.TimeEntry.end_time.is_(None))
    
    return query.all()


def get_project_time_entries(db: Session, project_id: uuid.UUID):
    """Get all time entries for a project"""
    return db.query(models.TimeEntry).filter(
        models.TimeEntry.project_id == project_id,
        models.TimeEntry.is_deleted == False
    ).all()


def get_task_time_entries(db: Session, task_id: uuid.UUID):
    """Get all time entries for a task"""
    return db.query(models.TimeEntry).filter(
        models.TimeEntry.task_id == task_id,
        models.TimeEntry.is_deleted == False
    ).all()


def update_time_entry(db: Session, time_entry_id: uuid.UUID, update_data: TimeEntryUpdate):
    """Update time entry description"""
    db_time_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.id == time_entry_id
    ).first()
    
    if db_time_entry:
        if update_data.description is not None:
            db_time_entry.description = update_data.description
        
        db_time_entry.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_time_entry)
    
    return db_time_entry


def get_active_timer(db: Session, user_id: uuid.UUID):
    """Get currently active timer for user"""
    return db.query(models.TimeEntry).filter(
        models.TimeEntry.user_id == user_id,
        models.TimeEntry.end_time.is_(None),
        models.TimeEntry.is_deleted == False
    ).first()


def create_manual_time_entry(db: Session, user_id: uuid.UUID, project_id: uuid.UUID, task_id: uuid.UUID, 
                           start_time: datetime, end_time: datetime, description: str = None):
    """Create a completed time entry manually (not from timer)"""
    duration_minutes = (end_time - start_time).total_seconds() / 60
    
    db_time_entry = models.TimeEntry(
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_minutes,
        description=description,
        user_id=user_id,
        project_id=project_id,
        task_id=task_id
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def get_time_entries_by_date_range(db: Session, user_id: uuid.UUID, start_date: datetime, end_date: datetime):
    """Get time entries for a user within a date range"""
    return db.query(models.TimeEntry).filter(
        models.TimeEntry.user_id == user_id,
        models.TimeEntry.start_time >= start_date,
        models.TimeEntry.start_time <= end_date,
        models.TimeEntry.is_deleted == False
    ).all()


def get_workspace_time_entries(db: Session, workspace_id: uuid.UUID, start_date: datetime = None, end_date: datetime = None):
    """Get all time entries for a workspace (through projects)"""
    query = db.query(models.TimeEntry).join(models.Project).filter(
        models.Project.workspace_id == workspace_id,
        models.TimeEntry.is_deleted == False
    )
    
    if start_date:
        query = query.filter(models.TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(models.TimeEntry.start_time <= end_date)
    
    return query.all()


def soft_delete_time_entry(db: Session, time_entry_id: uuid.UUID):
    """Soft delete time entry"""
    db_time_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.id == time_entry_id
    ).first()
    
    if db_time_entry:
        db_time_entry.is_deleted = True
        db_time_entry.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False
