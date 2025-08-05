# Workspace CRUD operations
from sqlalchemy.orm import Session
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
        models.Workspace.is_deleted == False
    ).all()


def get_workspace_by_id(db: Session, workspace_id: uuid.UUID):
    """Get workspace with members"""
    return db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id,
        models.Workspace.is_deleted == False
    ).first()


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
    # 2-TIER LOGIC: Force all new members to be MEMBER role
    db_member = models.WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_data.user_id,
        role=WorkspaceRole.MEMBER  # Always MEMBER, ignore member_data.role
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
    """Remove member from workspace"""
    db_member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == user_id
    ).first()

    if db_member:
        db.delete(db_member)
        db.commit()
        return True
    return False


def check_workspace_permission(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID, required_role: WorkspaceRole = WorkspaceRole.MEMBER):
    """Check if user has required permission in workspace"""
    member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == user_id,
        models.WorkspaceMember.role >= required_role
    ).first()

    return member is not None


def get_workspace_members(db: Session, workspace_id: uuid.UUID):
    """Get all members of a workspace"""
    return db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id
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
