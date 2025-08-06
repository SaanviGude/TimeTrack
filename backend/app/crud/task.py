# Task CRUD operations
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models
from ..schemas.task import TaskCreate, TaskUpdate, TaskStatus
from ..schemas.project import ProjectRole
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


#def create_subtask(db: Session, parent_task_id: uuid.UUID, subtask: TaskCreate):
    #"""Create subtask under a parent task"""
    # Override project_id and parent_task_id for subtask
    #subtask.project_id = None  # Subtasks don't directly belong to projects
    #subtask.parent_task_id = parent_task_id
    
    #return create_task(db, subtask)


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
    """Assign task to a user (must be project member)"""
    from fastapi import HTTPException
    
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    
    if not db_task:
        raise HTTPException(404, "Task not found")
    
    # Get project ID (handle subtasks)
    project_id = db_task.project_id
    if not project_id and db_task.parent_task_id:
        parent_task = get_task_by_id(db, db_task.parent_task_id)
        project_id = parent_task.project_id if parent_task else None
    
    if not project_id:
        raise HTTPException(400, "Task is not associated with any project")
    
    # Validate that user is a member of the project
    is_project_member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.is_deleted == False
    ).first()
    
    if not is_project_member:
        raise HTTPException(400, "Cannot assign task to user who is not a project member")
    
    # Assign the task
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


def check_task_access(db: Session, task_id: str, user_id: str, required_role: ProjectRole = ProjectRole.MEMBER):
    """
    2-TIER TASK SYSTEM with WORKSPACE OWNER OVERSIGHT:
    - Workspace Owner = MANAGER (automatic oversight of all tasks)
    - Project Creator = MANAGER (all tasks in their projects)
    - Project Members = MEMBER (limited task access)
    - Task Creator = always has access to their own tasks
    - Task Assignee = always has access to assigned tasks
    """
    from fastapi import HTTPException
    
    # Parse task UUID
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(400, f"Invalid task ID format: {task_id}")

    # Parse user UUID
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(400, "Invalid user ID format")

    # Get task
    task = get_task_by_id(db, task_uuid)
    if not task:
        raise HTTPException(404, "Task not found")

    # For subtasks, get the root project through parent task chain
    project_id = task.project_id
    if not project_id and task.parent_task_id:
        # Follow parent chain to find project
        current_task = task
        while current_task.parent_task_id and not current_task.project_id:
            current_task = get_task_by_id(db, current_task.parent_task_id)
            if not current_task:
                break
        project_id = current_task.project_id if current_task else None

    if not project_id:
        raise HTTPException(404, "Task is not associated with any project")

    # Check if user is workspace owner (automatic MANAGER access)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    workspace_owner = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id,
        models.Workspace.owner_id == user_uuid
    ).first()

    if workspace_owner:
        user_effective_role = ProjectRole.MANAGER
    else:
        # Check if user is project creator (MANAGER access)
        is_project_creator = project.creator_id == user_uuid

        if is_project_creator:
            user_effective_role = ProjectRole.MANAGER
        else:
            # Check if user is project member
            is_project_member = db.query(models.ProjectMember).filter(
                models.ProjectMember.project_id == project_id,
                models.ProjectMember.user_id == user_uuid,
                models.ProjectMember.is_deleted == False
            ).first()

            if is_project_member:
                # Get the actual role from project membership
                user_effective_role = is_project_member.role
            else:
                # Check if user is task creator or assignee (special access)
                is_task_creator = task.created_by == user_uuid if hasattr(task, 'created_by') else False
                is_task_assignee = task.assigned_to_id == user_uuid

                if is_task_creator or is_task_assignee:
                    user_effective_role = ProjectRole.MEMBER
                else:
                    raise HTTPException(403, "Not authorized to access this task")

    # Check permission level (MANAGER=1, MEMBER=2, lower = higher privilege)
    if user_effective_role <= required_role:
        # Additional check for MEMBER access - they can only access assigned tasks
        if user_effective_role == ProjectRole.MEMBER and required_role == ProjectRole.MEMBER:
            is_assigned = task.assigned_to_id == user_uuid
            is_unassigned = task.assigned_to_id is None
            
            # Members can only access tasks assigned to them OR unassigned tasks (for viewing)
            # BUT they cannot access tasks assigned to other users
            if task.assigned_to_id is not None and task.assigned_to_id != user_uuid:
                raise HTTPException(403, "Members cannot access tasks assigned to other users")
        
        return task
    else:
        role_name = "manager" if required_role == ProjectRole.MANAGER else "member"
        raise HTTPException(403, f"{role_name.title()} access required")


def get_workspace_tasks(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID):
    """Get tasks in workspace based on user role"""
    # Check if user is workspace owner
    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id,
        models.Workspace.owner_id == user_id
    ).first()

    if workspace:
        # Workspace owner sees ALL tasks in workspace
        return db.query(models.Task).join(models.Project).filter(
            models.Project.workspace_id == workspace_id,
            models.Task.is_deleted == False,
            models.Project.is_deleted == False
        ).all()
    else:
        # Regular user sees only accessible tasks
        return get_user_accessible_tasks(db, user_id, workspace_id)


def get_user_accessible_tasks(db: Session, user_id: uuid.UUID, workspace_id: uuid.UUID = None):
    """Get tasks accessible to user based on role"""
    
    # Check if user is project manager for any projects
    manager_projects = db.query(models.ProjectMember).filter(
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.role == ProjectRole.MANAGER,
        models.ProjectMember.is_deleted == False
    ).all()
    
    accessible_tasks = []
    
    # Add ALL tasks from projects where user is MANAGER
    for membership in manager_projects:
        project_tasks = db.query(models.Task).filter(
            models.Task.project_id == membership.project_id,
            models.Task.is_deleted == False
        ).all()
        accessible_tasks.extend(project_tasks)
    
    # Add ONLY ASSIGNED tasks from projects where user is MEMBER
    member_projects = db.query(models.ProjectMember).filter(
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.role == ProjectRole.MEMBER,
        models.ProjectMember.is_deleted == False
    ).all()
    
    for membership in member_projects:
        # Only assigned tasks for members
        assigned_tasks = db.query(models.Task).filter(
            models.Task.project_id == membership.project_id,
            models.Task.assigned_to_id == user_id,
            models.Task.is_deleted == False
        ).all()
        accessible_tasks.extend(assigned_tasks)
        
        # NOTE: Members should NOT see unassigned tasks in bulk queries
        # They can only view unassigned tasks when specifically requested via check_task_access
    
    # Remove duplicates and apply workspace filter
    unique_tasks = {task.id: task for task in accessible_tasks}
    
    if workspace_id:
        filtered_tasks = []
        for task in unique_tasks.values():
            project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
            if project and project.workspace_id == workspace_id:
                filtered_tasks.append(task)
        return filtered_tasks
    
    return list(unique_tasks.values())


def get_user_tasks_enhanced(db: Session, user_id: uuid.UUID, status: TaskStatus = None, include_accessible: bool = False):
    """Enhanced user tasks - can include accessible tasks beyond just assigned"""
    if include_accessible:
        tasks = get_user_accessible_tasks(db, user_id)
        if status:
            tasks = [task for task in tasks if task.status == status]
        return tasks
    else:
        # Original behavior - just assigned tasks
        return get_user_tasks(db, user_id, status)
