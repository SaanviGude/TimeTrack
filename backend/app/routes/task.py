from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models
from ..crud.task import (
    create_task, get_project_tasks, get_task_by_id, get_user_tasks,
    update_task, get_task_subtasks, update_task_status,
    assign_task, unassign_task, soft_delete_task, check_task_access,
    get_workspace_tasks, get_user_accessible_tasks, get_user_tasks_enhanced
)
from ..crud.project import check_project_access
from ..crud.workspace import is_workspace_owner
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
    """Create a new task in a project - requires MANAGER role"""
    # Check if user has MANAGER access to the project (for top-level tasks)
    if task.project_id:
        check_project_access(db, str(task.project_id), str(current_user.id), required_role=ProjectRole.MANAGER)
    
    # For subtasks, check MANAGER access to parent task's project
    if task.parent_task_id:
        parent_task = get_task_by_id(db, task.parent_task_id)
        if not parent_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent task not found"
            )
        # Use task access check for parent task with MANAGER requirement
        check_task_access(db, str(task.parent_task_id), str(current_user.id), required_role=ProjectRole.MANAGER)
    
    return create_task(db, task)


@router.get("/project/{project_id}", response_model=List[TaskResponse])
def list_project_tasks(
    project_id: str,
    include_subtasks: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks in a project with role-based filtering"""
    import uuid
    project_uuid = uuid.UUID(project_id)
    
    # Check if user has access to the project using new 2-tier system
    project = check_project_access(db, project_id, str(current_user.id))
    
    # Check if user is workspace owner for enhanced visibility
    if is_workspace_owner(db, project.workspace_id, current_user.id):
        # Workspace owner sees ALL tasks
        return get_project_tasks(db, project_uuid, include_subtasks)
    else:
        # Check if user is project manager
        is_project_manager = db.query(models.ProjectMember).filter(
            models.ProjectMember.project_id == project_uuid,
            models.ProjectMember.user_id == current_user.id,
            models.ProjectMember.role == ProjectRole.MANAGER,
            models.ProjectMember.is_deleted == False
        ).first()
        
        if is_project_manager:
            # Project manager sees ALL tasks
            return get_project_tasks(db, project_uuid, include_subtasks)
        else:
            # Regular member sees ASSIGNED tasks and UNASSIGNED tasks (for viewing)
            all_tasks = get_project_tasks(db, project_uuid, include_subtasks)
            
            # Filter to show tasks assigned to this member OR unassigned tasks
            member_tasks = [
                task for task in all_tasks 
                if task.assigned_to_id == current_user.id or task.assigned_to_id is None
            ]
            
            # If subtasks are included, filter subtasks for each task based on member permissions
            if include_subtasks:
                for task in member_tasks:
                    if hasattr(task, 'subtasks') and task.subtasks:
                        # Filter subtasks - members only see subtasks assigned to them OR unassigned
                        filtered_subtasks = [
                            subtask for subtask in task.subtasks
                            if subtask.assigned_to_id == current_user.id or subtask.assigned_to_id is None
                        ]
                        task.subtasks = filtered_subtasks
            
            return member_tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_details(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task details with filtered subtasks based on user permissions"""
    import uuid
    
    # Check access to the task
    task = check_task_access(db, task_id, str(current_user.id))
    
    # Get all subtasks for this task
    task_uuid = uuid.UUID(task_id)
    all_subtasks = get_task_subtasks(db, task_uuid)
    
    # Apply member filtering for subtasks (same logic as list_task_subtasks)
    project_id = task.project_id
    if not project_id:
        raise HTTPException(500, "Task not associated with project")
    
    # Check if user is workspace owner
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project and is_workspace_owner(db, project.workspace_id, current_user.id):
        filtered_subtasks = all_subtasks  # Workspace owner sees all
    else:
        # Check if user is project manager
        is_project_manager = db.query(models.ProjectMember).filter(
            models.ProjectMember.project_id == project_id,
            models.ProjectMember.user_id == current_user.id,
            models.ProjectMember.role == ProjectRole.MANAGER,
            models.ProjectMember.is_deleted == False
        ).first()
        
        if is_project_manager:
            filtered_subtasks = all_subtasks  # Project manager sees all
        else:
            # Member sees only subtasks assigned to them OR unassigned subtasks
            filtered_subtasks = [
                subtask for subtask in all_subtasks 
                if subtask.assigned_to_id == current_user.id or subtask.assigned_to_id is None
            ]
    
    # Replace the task's subtasks with filtered ones
    task.subtasks = filtered_subtasks
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task_details(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task details (manager access or task creator)"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    # Use comprehensive task access check - allows workspace owner, project manager, or task access
    task = check_task_access(db, task_id, str(current_user.id))
    
    updated_task = update_task(db, task_uuid, task_update)
    return updated_task


@router.put("/{task_id}/status")
def update_task_status_endpoint(
    task_id: str,
    status: TaskStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status (accessible to task assignee, creator, or project managers)"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    # Use comprehensive task access check - allows multiple access paths
    task = check_task_access(db, task_id, str(current_user.id))
    
    updated_task = update_task_status(db, task_uuid, status)
    return {"message": "Task status updated successfully", "new_status": status}


@router.put("/{task_id}/assign/{user_id}")
def assign_task_to_user(
    task_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign task to a user (manager access required)"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    user_uuid = uuid.UUID(user_id)
    
    # Check manager access using new 2-tier system
    task = check_task_access(db, task_id, str(current_user.id), ProjectRole.MANAGER)
    
    # Validation is now handled in the assign_task CRUD function
    updated_task = assign_task(db, task_uuid, user_uuid)
    return {"message": "Task assigned successfully"}


@router.put("/{task_id}/unassign")
def unassign_task_from_user(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove task assignment (manager access required)"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    # Check manager access using new 2-tier system
    task = check_task_access(db, task_id, str(current_user.id), ProjectRole.MANAGER)
    
    updated_task = unassign_task(db, task_uuid)
    return {"message": "Task unassigned successfully"}


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete task and all its subtasks (manager access required)"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    # Check manager access using new 2-tier system
    task = check_task_access(db, task_id, str(current_user.id), ProjectRole.MANAGER)
    
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
    """Get all subtasks for a parent task with role-based filtering"""
    import uuid
    task_uuid = uuid.UUID(task_id)
    
    # Check access to parent task
    task = check_task_access(db, task_id, str(current_user.id))
    
    # Get all child tasks
    all_subtasks = get_task_subtasks(db, task_uuid)
    
    # Apply member filtering for subtasks
    project_id = task.project_id
    if not project_id:
        raise HTTPException(500, "Task not associated with project")
    
    # Check if user is workspace owner
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project and is_workspace_owner(db, project.workspace_id, current_user.id):
        return all_subtasks  # Workspace owner sees all
    
    # Check if user is project manager
    is_project_manager = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id,
        models.ProjectMember.role == ProjectRole.MANAGER,
        models.ProjectMember.is_deleted == False
    ).first()
    
    if is_project_manager:
        return all_subtasks  # Project manager sees all
    else:
        # Member sees subtasks assigned to them OR unassigned subtasks
        member_subtasks = [
            subtask for subtask in all_subtasks 
            if subtask.assigned_to_id == current_user.id or subtask.assigned_to_id is None
        ]
        return member_subtasks
