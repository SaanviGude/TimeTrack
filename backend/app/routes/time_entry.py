from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from ..database import get_db
from ..crud.time_entry import (
    start_time_entry, get_user_time_entries, get_task_time_entries,
    update_time_entry, get_active_timer, stop_time_entry,
    get_time_entries_by_date_range, soft_delete_time_entry,
    create_manual_time_entry
)

from ..crud.task import get_task_by_id
from ..crud.project import check_project_permission
from ..schemas.time_entry import (
    TimeEntryCreate, TimeEntryResponse, TimeEntryUpdate, TimeEntryTimerStart
)
from ..schemas.project import ProjectRole
from .auth import get_current_user
from ..models.user import User
from ..models.time_entry import TimeEntry

router = APIRouter()

# Helper function to get time entry by ID


def get_time_entry_by_id(db: Session, time_entry_id):
    """Get time entry by ID"""
    return db.query(TimeEntry).filter(
        TimeEntry.id == time_entry_id,
        TimeEntry.is_deleted == False
    ).first()


@router.post("/", response_model=TimeEntryResponse)
def create_new_time_entry(
    time_entry: TimeEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new time entry"""
    # Verify task exists and user has access
    if time_entry.task_id:
        task = get_task_by_id(db, time_entry.task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if user has access to the project or is assigned to the task
        has_project_access = task.project_id and check_project_permission(
            db, task.project_id, current_user.id)
        is_assigned = task.assigned_to_id == current_user.id

        if not (has_project_access or is_assigned):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to log time for this task"
            )

    # Set user_id to current user
    time_entry.user_id = current_user.id

    return start_time_entry(db, time_entry)


@router.get("/my-entries", response_model=List[TimeEntryResponse])
def list_my_time_entries(
    start_date: Optional[date] = Query(
        None, description="Filter entries from this date"),
    end_date: Optional[date] = Query(
        None, description="Filter entries until this date"),
    task_id: Optional[str] = Query(
        None, description="Filter entries for specific task"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's time entries with optional filters"""
    # Get entries based on date range if provided
    if start_date and end_date:
        from datetime import datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        entries = get_time_entries_by_date_range(
            db, current_user.id, start_datetime, end_datetime)
    else:
        entries = get_user_time_entries(db, current_user.id)

    # Filter by task if specified
    if task_id:
        import uuid
        task_uuid = uuid.UUID(task_id)

        # Verify user has access to the task
        task = get_task_by_id(db, task_uuid)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        has_project_access = task.project_id and check_project_permission(
            db, task.project_id, current_user.id)
        is_assigned = task.assigned_to_id == current_user.id

        if not (has_project_access or is_assigned):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view time entries for this task"
            )

        # Filter entries by task
        entries = [entry for entry in entries if entry.task_id == task_uuid]

    return entries


@router.get("/daily/{date}", response_model=List[TimeEntryResponse])
def get_daily_entries(
    date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time entries for a specific date"""
    from datetime import datetime, timedelta
    start_datetime = datetime.combine(date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)
    return get_time_entries_by_date_range(db, current_user.id, start_datetime, end_datetime)


@router.get("/task/{task_id}", response_model=List[TimeEntryResponse])
def list_task_time_entries(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all time entries for a specific task"""
    import uuid
    task_uuid = uuid.UUID(task_id)

    # Verify task exists and user has access
    task = get_task_by_id(db, task_uuid)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check if user has access to the project
    if task.project_id and not check_project_permission(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view time entries for this task"
        )

    return get_task_time_entries(db, task_uuid)


@router.get("/{time_entry_id}", response_model=TimeEntryResponse)
def get_time_entry_details(
    time_entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time entry details"""
    import uuid
    entry_uuid = uuid.UUID(time_entry_id)

    time_entry = get_time_entry_by_id(db, entry_uuid)
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )

    # Check if user owns this time entry or has project access
    if time_entry.user_id != current_user.id:
        # Check if user has access to the project
        if time_entry.task and time_entry.task.project_id:
            if not check_project_permission(db, time_entry.task.project_id, current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this time entry"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this time entry"
            )

    return time_entry


@router.put("/{time_entry_id}", response_model=TimeEntryResponse)
def update_time_entry_details(
    time_entry_id: str,
    time_entry_update: TimeEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update time entry details"""
    import uuid
    entry_uuid = uuid.UUID(time_entry_id)

    time_entry = get_time_entry_by_id(db, entry_uuid)
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )

    # Only owner can update their time entries
    if time_entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own time entries"
        )

    updated_entry = update_time_entry(db, entry_uuid, time_entry_update)
    return updated_entry


@router.delete("/{time_entry_id}")
def delete_time_entry_record(
    time_entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete time entry"""
    import uuid
    entry_uuid = uuid.UUID(time_entry_id)

    time_entry = get_time_entry_by_id(db, entry_uuid)
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )

    # Only owner can delete their time entries
    if time_entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own time entries"
        )

    success = soft_delete_time_entry(db, entry_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete time entry"
        )

    return {"message": "Time entry deleted successfully"}


# Timer endpoints - Simplified
@router.post("/timer/start")
def start_time_timer(
    timer_data: TimeEntryTimerStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a timer for a task"""
    # Verify task exists and user has access
    if timer_data.task_id:
        task = get_task_by_id(db, timer_data.task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if user has access to the project or is assigned to the task
        has_project_access = task.project_id and check_project_permission(
            db, task.project_id, current_user.id)
        is_assigned = task.assigned_to_id == current_user.id

        if not (has_project_access or is_assigned):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to track time for this task"
            )

    # Check if user already has an active timer
    active_timer = get_active_timer(db, current_user.id)
    if active_timer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active timer. Stop it before starting a new one."
        )

    # Create TimeEntryCreate object with user_id set
    time_entry = TimeEntryCreate(
        user_id=current_user.id,
        task_id=timer_data.task_id,
        project_id=timer_data.project_id,
        description=timer_data.description,
        start_time=timer_data.start_time
    )
    
    timer = start_time_entry(db, time_entry)
    return {"message": "Timer started successfully", "time_entry": timer}


@router.post("/timer/stop", response_model=TimeEntryResponse)
def stop_time_timer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop the active timer and create time entry"""
    active_timer = get_active_timer(db, current_user.id)
    if not active_timer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active timer found"
        )

    # Calculate duration and stop timer
    from datetime import datetime, timezone
    from ..schemas.time_entry import TimeEntryStop

    end_time = datetime.now(timezone.utc)
    duration = (end_time - active_timer.start_time).total_seconds() / 60

    stop_data = TimeEntryStop(end_time=end_time, duration_minutes=duration)
    time_entry = stop_time_entry(db, active_timer.id, stop_data)
    return time_entry


@router.get("/timer/active")
def get_active_time_timer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current active timer"""
    active_timer = get_active_timer(db, current_user.id)
    if active_timer:
        return {"active": True, "time_entry": active_timer}
    return {"active": False, "time_entry": None}


# Simple statistics endpoint using existing functions
@router.get("/statistics")
def get_time_tracking_statistics(
    start_date: Optional[date] = Query(
        None, description="Statistics from this date"),
    end_date: Optional[date] = Query(
        None, description="Statistics until this date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time tracking statistics for current user"""
    if start_date and end_date:
        from datetime import datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        entries = get_time_entries_by_date_range(
            db, current_user.id, start_datetime, end_datetime)
    else:
        entries = get_user_time_entries(db, current_user.id)

    total_minutes = sum(entry.duration_minutes or 0 for entry in entries)
    total_entries = len(entries)

    return {
        "total_time_minutes": total_minutes,
        "total_entries": total_entries,
        "entries": entries
    }
