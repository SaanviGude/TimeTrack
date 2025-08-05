from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models
from ..crud.project import (
    create_project, get_workspace_projects, get_user_projects, get_project_by_id,
    update_project, add_project_member, update_project_member_role,
    remove_project_member, get_project_members,
    soft_delete_project, check_project_access, get_user_accessible_projects
)
from ..crud.workspace import check_workspace_access, is_workspace_owner
from ..schemas.project import (
    ProjectCreate, ProjectResponse, ProjectUpdate,
    ProjectMemberCreate, ProjectMemberResponse, ProjectRole
)
from ..schemas.workspace import WorkspaceRole
from .auth import get_current_user
from ..models.user import User

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project within a workspace"""
    # Check if user has access to the workspace using new 2-tier system
    check_workspace_access(db, str(project.workspace_id), str(current_user.id))

    return create_project(db, project, current_user.id)


@router.get("/workspace/{workspace_id}", response_model=List[ProjectResponse])
def list_workspace_projects(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get projects in a workspace (all for owners, accessible for members)"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)

    # Check if user has access to the workspace using new 2-tier system
    check_workspace_access(db, workspace_id, str(current_user.id))

    # Check if user is workspace owner
    if is_workspace_owner(db, workspace_uuid, current_user.id):
        # Workspace owner sees ALL projects
        return get_workspace_projects(db, workspace_uuid)
    else:
        # Regular member sees only projects they created or are members of
        return get_user_accessible_projects(db, current_user.id, workspace_uuid)


@router.get("/my-projects", response_model=List[ProjectResponse])
def list_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects where user is a member"""
    return get_user_projects(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_details(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details with members"""
    # Use new 2-tier access check with workspace owner oversight
    project = check_project_access(db, project_id, str(current_user.id))
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project_details(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project details (manager only)"""
    # Check manager access and get project using new 2-tier system
    project = check_project_access(
        db, project_id, str(current_user.id), ProjectRole.MANAGER)

    updated_project = update_project(db, project.id, project_update)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return updated_project


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete project (manager only)"""
    import uuid

    # Check manager access using new 2-tier system
    project = check_project_access(
        db, project_id, str(current_user.id), ProjectRole.MANAGER)

    success = soft_delete_project(db, project.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def add_member_to_project(
    project_id: str,
    member_data: ProjectMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add member to project as MEMBER role (manager only)"""
    # Check manager access using new 2-tier system
    project = check_project_access(
        db, project_id, str(current_user.id), ProjectRole.MANAGER)

    # 2-TIER LOGIC: Override any role request to MEMBER
    member_create = ProjectMemberCreate(
        user_id=member_data.user_id,
        role=ProjectRole.MEMBER  # Force MEMBER role
    )

    return add_project_member(db, project.id, member_create)


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def list_project_members(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of project (manager only)"""
    # Check manager access using new 2-tier system
    project = check_project_access(
        db, project_id, str(current_user.id), ProjectRole.MANAGER)

    return get_project_members(db, project.id)


@router.put("/{project_id}/members/{user_id}")
def update_project_member_role_endpoint(
    project_id: str,
    user_id: str,
    role: ProjectRole,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role in project (manager only, with workspace owner protection)"""
    import uuid

    # Check manager access using new 2-tier system
    project = check_project_access(
        db, project_id, str(current_user.id), ProjectRole.MANAGER)

    member_uuid = uuid.UUID(user_id)

    # Get workspace info for protection checks
    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id
    ).first()

    # PROTECTION: Check if trying to modify workspace owner
    is_target_workspace_owner = workspace and workspace.owner_id == member_uuid
    is_requester_workspace_owner = workspace and workspace.owner_id == current_user.id

    if is_target_workspace_owner and not is_requester_workspace_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify workspace owner's role. Only workspace owner has this privilege."
        )

    if is_target_workspace_owner and role != ProjectRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workspace owner must always remain as MANAGER"
        )

    # Pass requester_id for additional protection in CRUD
    updated_member = update_project_member_role(
        db, project.id, member_uuid, role, current_user.id)

    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return {"message": "Member role updated successfully"}


@router.delete("/{project_id}/members/{user_id}")
def remove_member_from_project(
    project_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from project (manager only, with workspace owner protection)"""
    import uuid

    # Check manager access using new 2-tier system
    project = check_project_access(
        db, project_id, str(current_user.id), ProjectRole.MANAGER)

    # Parse member UUID
    try:
        member_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {user_id}"
        )

    # Get workspace info for protection checks
    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id
    ).first()

    # PROTECTION: Cannot remove workspace owner
    is_target_workspace_owner = workspace and workspace.owner_id == member_uuid
    if is_target_workspace_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove workspace owner from project. Workspace owner has permanent oversight access."
        )

    # PROTECTION: Cannot remove project creator
    if project.creator_id == member_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove project creator. Creator always remains as manager."
        )

    # Pass requester_id for additional protection in CRUD
    success = remove_project_member(
        db, project.id, member_uuid, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return {"message": "Member removed successfully"}
