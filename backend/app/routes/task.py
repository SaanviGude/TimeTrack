from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..crud.task import (
    create_task, get_project_tasks, get_task_by_id, get_user_tasks,
    update_task, get_task_subtasks, create_subtask, update_task_status,
    assign_task, unassign_task, soft_delete_task
)
from ..crud.project import check_project_permission
from ..schemas.task import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus
)
from ..schemas.project import ProjectRole
from .auth import get_current_user
from ..models.user import User

router = APIRouter()


@router.post("/", response_model=TaskResponse)
def create_new_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task in a project"""
    # Check if user has access to the project (for top-level tasks)
    if task.project_id and not check_project_permission(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks in this project"
        )
    
    # For subtasks, check access to parent task's project
    if task.parent_task_id:
        parent_task = get_task_by_id(db, task.parent_task_id)
        if not parent_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent task not found"
            )
        if parent_task.project_id and not check_project_permission(db, parent_task.project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create subtasks in this project"
            )
    
    return create_task(db, task)


@router.get("/project/{project_id}", response_model=List[TaskResponse])
def list_project_tasks(
    project_id: str,
    include_subtasks: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks in a project"""
    import uuid
    project_uuid = uuid.UUID(project_id)
    
    # Check if user has access to the project
    if not check_project_permission(db, project_uuid, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return get_project_tasks(db, project_uuid, include_subtasks)


@router.get("/my-tasks", response_model=List[TaskResponse])
def list_user_tasks(
    status: Optional[TaskStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks assigned to current user"""
    return get_user_tasks(db, current_user.id, status)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_details(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task details with subtasks"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
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
            detail="Not authorized to access this task"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task_details(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task details"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
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
            detail="Not authorized to update this task"
        )
    
    updated_task = update_task(db, task_uuid, task_update)
    return updated_task


@router.put("/{task_id}/status")
def update_task_status_endpoint(
    task_id: str,
    status: TaskStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    task = get_task_by_id(db, task_uuid)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project or is assigned to the task
    has_project_access = task.project_id and check_project_permission(db, task.project_id, current_user.id)
    is_assigned = task.assigned_to_id == current_user.id
    
    if not (has_project_access or is_assigned):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task status"
        )
    
    updated_task = update_task_status(db, task_uuid, status)
    return {"message": "Task status updated successfully", "new_status": status}


@router.put("/{task_id}/assign/{user_id}")
def assign_task_to_user(
    task_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign task to a user"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    user_uuid = uuid.UUID(user_id)
    
    task = get_task_by_id(db, task_uuid)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has manager access to the project
    if task.project_id and not check_project_permission(db, task.project_id, current_user.id, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required to assign tasks"
        )
    
    updated_task = assign_task(db, task_uuid, user_uuid)
    return {"message": "Task assigned successfully"}


@router.put("/{task_id}/unassign")
def unassign_task_from_user(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove task assignment"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    task = get_task_by_id(db, task_uuid)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has manager access to the project
    if task.project_id and not check_project_permission(db, task.project_id, current_user.id, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required to unassign tasks"
        )
    
    updated_task = unassign_task(db, task_uuid)
    return {"message": "Task unassigned successfully"}


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete task and all its subtasks"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    task = get_task_by_id(db, task_uuid)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has manager access to the project
    if task.project_id and not check_project_permission(db, task.project_id, current_user.id, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required to delete tasks"
        )
    
    success = soft_delete_task(db, task_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete task"
        )
    
    return {"message": "Task deleted successfully"}


@router.get("/{task_id}/subtasks", response_model=List[TaskResponse])
def list_task_subtasks(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subtasks for a parent task"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
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
            detail="Not authorized to access this task"
        )
    
    return get_task_subtasks(db, task_uuid)


@router.post("/{task_id}/subtasks", response_model=TaskResponse)
def create_task_subtask(
    task_id: str,
    subtask: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a subtask under a parent task"""
    import uuid
    parent_task_uuid = uuid.UUID(task_id)
    
    parent_task = get_task_by_id(db, parent_task_uuid)
    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found"
        )
    
    # Check if user has access to the project
    if parent_task.project_id and not check_project_permission(db, parent_task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create subtasks in this project"
        )
    
    return create_subtask(db, parent_task_uuid, subtask)
