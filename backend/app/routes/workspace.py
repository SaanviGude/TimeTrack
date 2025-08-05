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


def check_workspace_access(db: Session, workspace_id: str, user_id: str, required_role: WorkspaceRole = WorkspaceRole.MEMBER):
    """
    Helper function to check workspace access with proper ownership and membership validation.
    Returns the workspace if access is granted, raises HTTPException otherwise.
    """
    import uuid

    # Parse workspace UUID
    try:
        workspace_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid workspace ID format: {workspace_id}"
        )

    # Parse user UUID
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Check if workspace exists
    workspace = get_workspace_by_id(db, workspace_uuid)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check access: owner always has admin access, otherwise check membership
    is_owner = workspace.owner_id == user_uuid
    if is_owner:
        # Owner always has access to everything
        return workspace

    # Check membership permissions
    has_member_access = check_workspace_permission(
        db, workspace_uuid, user_uuid, required_role)
    if has_member_access:
        return workspace

    # No access granted
    role_name = "admin" if required_role == WorkspaceRole.ADMIN else "member"
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"{role_name.title()} access required"
    )


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

    try:
        workspace_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid workspace ID format: {workspace_id}"
        )

    # Check if user has access to this workspace (either as owner or member)
    try:
        user_uuid = uuid.UUID(str(current_user.id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # First check if workspace exists
    workspace = get_workspace_by_id(db, workspace_uuid)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if user is the owner or has member access
    is_owner = workspace.owner_id == user_uuid
    has_member_access = check_workspace_permission(
        db, workspace_uuid, user_uuid)

    if not (is_owner or has_member_access):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workspace"
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
    # Check admin access and get workspace
    workspace = check_workspace_access(
        db, workspace_id, current_user.id, WorkspaceRole.ADMIN)

    updated_workspace = update_workspace(db, workspace.id, workspace_update)
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
    # Check admin access and get workspace
    workspace = check_workspace_access(
        db, workspace_id, current_user.id, WorkspaceRole.ADMIN)

    success = soft_delete_workspace(db, workspace.id)
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
    # Check admin access and get workspace
    workspace = check_workspace_access(
        db, workspace_id, current_user.id, WorkspaceRole.ADMIN)

    return add_workspace_member(db, workspace.id, member_data)


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
def list_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of workspace (admin only)"""
    # Check admin access and get workspace
    workspace = check_workspace_access(
        db, workspace_id, current_user.id, WorkspaceRole.ADMIN)

    return get_workspace_members(db, workspace.id)


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

    # Check admin access and get workspace
    workspace = check_workspace_access(
        db, workspace_id, current_user.id, WorkspaceRole.ADMIN)

    # Parse member UUID
    try:
        member_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {user_id}"
        )

    updated_member = update_member_role(db, workspace.id, member_uuid, role)
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

    # Check admin access and get workspace
    workspace = check_workspace_access(
        db, workspace_id, current_user.id, WorkspaceRole.ADMIN)

    # Parse member UUID
    try:
        member_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {user_id}"
        )

    success = remove_workspace_member(db, workspace.id, member_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return {"message": "Member removed successfully"}
