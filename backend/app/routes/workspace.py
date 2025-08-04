from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud.workspace import (
    create_workspace, get_user_workspaces, get_workspace_by_id,
    update_workspace, add_workspace_member, update_member_role,
    remove_workspace_member, check_workspace_permission, get_workspace_members,
    soft_delete_workspace
)
from ..schemas.workspace import (
    WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate,
    WorkspaceMemberCreate, WorkspaceMemberResponse, WorkspaceRole
)
from .auth import get_current_user
from ..models.user import User

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse)
def create_new_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace with current user as owner"""
    return create_workspace(db, workspace, current_user.id)


@router.get("/", response_model=List[WorkspaceResponse])
def list_user_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workspaces where user is owner or member"""
    return get_user_workspaces(db, current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace_details(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workspace details with members"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    
    # Check if user has access to this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workspace"
        )
    
    workspace = get_workspace_by_id(db, workspace_uuid)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace_details(
    workspace_id: str,
    workspace_update: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update workspace details (admin only)"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    
    # Check if user is admin of this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id, WorkspaceRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    updated_workspace = update_workspace(db, workspace_uuid, workspace_update)
    if not updated_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return updated_workspace


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete workspace (admin only)"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    
    # Check if user is admin of this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id, WorkspaceRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    success = soft_delete_workspace(db, workspace_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return {"message": "Workspace deleted successfully"}


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
def add_member_to_workspace(
    workspace_id: str,
    member_data: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add member to workspace (admin only)"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    
    # Check if user is admin of this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id, WorkspaceRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return add_workspace_member(db, workspace_uuid, member_data)


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
def list_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of workspace"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    
    # Check if user has access to this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workspace"
        )
    
    return get_workspace_members(db, workspace_uuid)


@router.put("/{workspace_id}/members/{user_id}")
def update_workspace_member_role(
    workspace_id: str,
    user_id: str,
    role: WorkspaceRole,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role in workspace (admin only)"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    member_uuid = uuid.UUID(user_id)
    
    # Check if user is admin of this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id, WorkspaceRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    updated_member = update_member_role(db, workspace_uuid, member_uuid, role)
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return {"message": "Member role updated successfully"}


@router.delete("/{workspace_id}/members/{user_id}")
def remove_member_from_workspace(
    workspace_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from workspace (admin only)"""
    import uuid
    workspace_uuid = uuid.UUID(workspace_id)
    member_uuid = uuid.UUID(user_id)
    
    # Check if user is admin of this workspace
    if not check_workspace_permission(db, workspace_uuid, current_user.id, WorkspaceRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    success = remove_workspace_member(db, workspace_uuid, member_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return {"message": "Member removed successfully"}
