# Workspace CRUD operations
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models
from ..schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceMemberCreate,
    WorkspaceMemberUpdate, WorkspaceRole
)
import uuid
from datetime import datetime


def create_workspace(db: Session, workspace: WorkspaceCreate, owner_id: uuid.UUID):
    """Create new workspace with user as owner"""
    db_workspace = models.Workspace(
        name=workspace.name,
        description=workspace.description,
        owner_id=owner_id
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)

    # Add owner as ADMIN member
    db_member = models.WorkspaceMember(
        workspace_id=db_workspace.id,
        user_id=owner_id,
        role=WorkspaceRole.ADMIN
    )
    db.add(db_member)
    db.commit()

    return db_workspace


def get_user_workspaces(db: Session, user_id: uuid.UUID):
    """Get all workspaces where user is owner or member"""
    return db.query(models.Workspace).join(models.WorkspaceMember).filter(
        models.WorkspaceMember.user_id == user_id,
        models.WorkspaceMember.is_deleted == False,
        models.Workspace.is_deleted == False
    ).all()


def get_workspace_by_id(db: Session, workspace_id: uuid.UUID):
    """Get workspace with members"""
    return db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id,
        models.Workspace.is_deleted == False
    ).first()


def is_workspace_owner(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID):
    """Check if user is workspace owner"""
    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id,
        models.Workspace.owner_id == user_id,
        models.Workspace.is_deleted == False
    ).first()
    return workspace is not None


def update_workspace(db: Session, workspace_id: uuid.UUID, workspace_update: WorkspaceUpdate):
    """Update workspace details"""
    db_workspace = db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id
    ).first()

    if db_workspace:
        update_data = workspace_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_workspace, key, value)

        db_workspace.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_workspace)

    return db_workspace


def add_workspace_member(db: Session, workspace_id: uuid.UUID, member_data: WorkspaceMemberCreate):
    """Add member to workspace (always as MEMBER in 2-tier system)"""
    # Check if user was previously a member (soft deleted)
    existing_member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == member_data.user_id
    ).first()

    if existing_member:
        if existing_member.is_deleted:
            # Reactivate previously deleted member
            existing_member.is_deleted = False
            existing_member.deleted_at = None
            existing_member.role = WorkspaceRole.MEMBER  # Force MEMBER role
            existing_member.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_member)
            return existing_member
        else:
            # Member already exists and is active
            return existing_member

    # Create new member
    db_member = models.WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_data.user_id,
        role=WorkspaceRole.MEMBER,  # Always MEMBER, ignore member_data.role
        is_deleted=False,
        deleted_at=None
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_member_role(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID, role: WorkspaceRole):
    """Update member role in workspace"""
    db_member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == user_id
    ).first()

    if db_member:
        db_member.role = role
        db_member.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_member)

    return db_member


def remove_workspace_member(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID):
    """Remove member from workspace (soft delete)"""
    db_member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == user_id,
        models.WorkspaceMember.is_deleted == False
    ).first()

    if db_member:
        db_member.is_deleted = True
        db_member.deleted_at = datetime.utcnow()
        db.commit()
        return True
    return False


def check_workspace_access(db: Session, workspace_id: str, user_id: str, required_role: WorkspaceRole = WorkspaceRole.MEMBER):
    """
    2-TIER WORKSPACE SYSTEM: Owner = ADMIN, Members = MEMBER
    Check if user has required access to workspace
    """

    # Parse workspace UUID
    try:
        workspace_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            400, f"Invalid workspace ID format: {workspace_id}")

    # Parse user UUID
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(400, "Invalid user ID format")

    # Get workspace
    workspace = get_workspace_by_id(db, workspace_uuid)
    if not workspace:
        raise HTTPException(404, "Workspace not found")

    # 2-TIER LOGIC: Owner = ADMIN, Members = MEMBER
    is_owner = workspace.owner_id == user_uuid

    if is_owner:
        user_effective_role = WorkspaceRole.ADMIN
    else:
        # Check if user is a member
        is_member = db.query(models.WorkspaceMember).filter(
            models.WorkspaceMember.workspace_id == workspace.id,
            models.WorkspaceMember.user_id == user_uuid,
            models.WorkspaceMember.is_deleted == False
        ).first()

        if is_member:
            user_effective_role = WorkspaceRole.MEMBER
        else:
            raise HTTPException(403, "Not a workspace member")

    # Check permission level (ADMIN=1, MEMBER=2, lower = higher privilege)
    if user_effective_role <= required_role:
        return workspace
    else:
        role_name = "admin" if required_role == WorkspaceRole.ADMIN else "member"
        raise HTTPException(403, f"{role_name.title()} access required")


def check_workspace_permission(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID, required_role: WorkspaceRole = WorkspaceRole.MEMBER):
    """Check if user has required permission in workspace"""
    member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == user_id,
        models.WorkspaceMember.role >= required_role,
        models.WorkspaceMember.is_deleted == False
    ).first()

    return member is not None


def get_workspace_members(db: Session, workspace_id: uuid.UUID):
    """Get all active members of a workspace"""
    return db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.is_deleted == False
    ).all()


def soft_delete_workspace(db: Session, workspace_id: uuid.UUID):
    """Soft delete workspace"""
    db_workspace = db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id
    ).first()

    if db_workspace:
        db_workspace.is_deleted = True
        db_workspace.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False
