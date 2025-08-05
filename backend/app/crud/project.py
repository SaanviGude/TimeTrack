# Project CRUD operations
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models
from ..schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectMemberCreate,
    ProjectMemberUpdate, ProjectRole, ProjectStatus
)
import uuid
from datetime import datetime


def check_project_access(db: Session, project_id: str, user_id: str, required_role: ProjectRole = ProjectRole.MEMBER):
    """
    2-TIER PROJECT SYSTEM with WORKSPACE OWNER OVERSIGHT:
    - Workspace Owner = MANAGER (automatic oversight)
    - Project Creator = MANAGER
    - Project Members = MEMBER
    """

    # Parse project UUID
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(400, f"Invalid project ID format: {project_id}")

    # Parse user UUID
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(400, "Invalid user ID format")

    # Get project
    project = get_project_by_id(db, project_uuid)
    if not project:
        raise HTTPException(404, "Project not found")

    # Check if user is workspace owner (automatic MANAGER access)
    workspace_owner = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id,
        models.Workspace.owner_id == user_uuid
    ).first()

    if workspace_owner:
        user_effective_role = ProjectRole.MANAGER
    else:
        # 2-TIER LOGIC: Creator = MANAGER, Members = MEMBER
        is_creator = project.creator_id == user_uuid

        if is_creator:
            user_effective_role = ProjectRole.MANAGER
        else:
            # Check if user is a member
            is_member = db.query(models.ProjectMember).filter(
                models.ProjectMember.project_id == project.id,
                models.ProjectMember.user_id == user_uuid,
                models.ProjectMember.is_deleted == False
            ).first()

            if is_member:
                user_effective_role = ProjectRole.MEMBER
            else:
                raise HTTPException(403, "Not a project member")

    # Check permission level (MANAGER=1, MEMBER=2, lower = higher privilege)
    if user_effective_role <= required_role:
        return project
    else:
        role_name = "manager" if required_role == ProjectRole.MANAGER else "member"
        raise HTTPException(403, f"{role_name.title()} access required")


def create_project(db: Session, project: ProjectCreate, creator_id: uuid.UUID):
    """Create new project within workspace and auto-add workspace owner as MANAGER"""
    db_project = models.Project(
        name=project.name,
        description=project.description,
        deadline=project.deadline,
        status=project.status,
        workspace_id=project.workspace_id,
        creator_id=creator_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Add creator as MANAGER (MUST BE COMMITTED)
    creator_member = models.ProjectMember(
        project_id=db_project.id,
        user_id=creator_id,
        role=ProjectRole.MANAGER
    )
    db.add(creator_member)
    db.commit()  # ← COMMIT CREATOR IMMEDIATELY
    db.refresh(creator_member)

    # Auto-add workspace owner as MANAGER (if different from creator)
    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id
    ).first()

    if workspace and workspace.owner_id != creator_id:
        # Check if workspace owner already exists as a member (soft delete scenario)
        existing_member = db.query(models.ProjectMember).filter(
            models.ProjectMember.project_id == db_project.id,
            models.ProjectMember.user_id == workspace.owner_id
        ).first()

        if existing_member:
            # Reactivate and set as MANAGER
            existing_member.is_deleted = False
            existing_member.deleted_at = None
            existing_member.role = ProjectRole.MANAGER
        else:
            # Add new workspace owner as MANAGER
            workspace_owner_member = models.ProjectMember(
                project_id=db_project.id,
                user_id=workspace.owner_id,
                role=ProjectRole.MANAGER
            )
            db.add(workspace_owner_member)

        db.commit()  # ← COMMIT WORKSPACE OWNER CHANGES

    return db_project


def get_workspace_projects(db: Session, workspace_id: uuid.UUID):
    """Get all projects in a workspace (for workspace owners)"""
    return db.query(models.Project).filter(
        models.Project.workspace_id == workspace_id,
        models.Project.is_deleted == False
    ).all()


def get_user_accessible_projects(db: Session, user_id: uuid.UUID, workspace_id: uuid.UUID):
    """Get projects accessible to a regular user (creator or member)"""
    return db.query(models.Project).join(models.ProjectMember).filter(
        models.Project.workspace_id == workspace_id,
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.is_deleted == False,
        models.Project.is_deleted == False
    ).all()


def get_user_projects(db: Session, user_id: uuid.UUID):
    """Get all projects where user is creator or member (across all workspaces)"""
    return db.query(models.Project).join(models.ProjectMember).filter(
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.is_deleted == False,
        models.Project.is_deleted == False
    ).all()


def get_project_by_id(db: Session, project_id: uuid.UUID):
    """Get project with members"""
    return db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.is_deleted == False
    ).first()


def update_project(db: Session, project_id: uuid.UUID, project_update: ProjectUpdate):
    """Update project details"""
    db_project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if db_project:
        update_data = project_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)

        db_project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_project)

    return db_project


def add_project_member(db: Session, project_id: uuid.UUID, member_data: ProjectMemberCreate):
    """Add member to project (always as MEMBER in 2-tier system)"""
    # Check if user was previously a member (soft deleted)
    existing_member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == member_data.user_id
    ).first()

    if existing_member:
        if existing_member.is_deleted:
            # Reactivate previously deleted member
            existing_member.is_deleted = False
            existing_member.deleted_at = None
            existing_member.role = ProjectRole.MEMBER  # Force MEMBER role
            existing_member.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_member)
            return existing_member
        else:
            # Member already exists and is active
            return existing_member

    # Create new member with MEMBER role only
    db_member = models.ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=ProjectRole.MEMBER,  # Always MEMBER, ignore member_data.role
        is_deleted=False,
        deleted_at=None
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_project_member_role(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, role: ProjectRole, requester_id: uuid.UUID):
    """Update member role in project with workspace owner protection"""

    # Get project and workspace info
    project = db.query(models.Project).filter(
        models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id).first()

    # Check if target user is workspace owner
    is_target_workspace_owner = workspace and workspace.owner_id == user_id
    is_requester_workspace_owner = workspace and workspace.owner_id == requester_id

    # PROTECTION: Only workspace owner can modify workspace owner's role
    if is_target_workspace_owner and not is_requester_workspace_owner:
        raise HTTPException(
            403, "Cannot modify workspace owner's role. Only workspace owner can change their own project access.")

    # PROTECTION: Prevent demoting workspace owner from MANAGER
    if is_target_workspace_owner and role != ProjectRole.MANAGER:
        raise HTTPException(
            403, "Workspace owner must always remain as MANAGER")

    # Find and update member
    db_member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_id
    ).first()

    if db_member:
        db_member.role = role
        db_member.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_member)

    return db_member


def remove_project_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, requester_id: uuid.UUID):
    """Remove member from project (soft delete) with workspace owner protection"""

    # Get project and workspace info
    project = db.query(models.Project).filter(
        models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == project.workspace_id).first()

    # PROTECTION: Cannot remove workspace owner
    is_target_workspace_owner = workspace and workspace.owner_id == user_id
    if is_target_workspace_owner:
        raise HTTPException(
            403, "Cannot remove workspace owner from project. Workspace owner has permanent oversight access.")

    # PROTECTION: Cannot remove project creator
    is_target_creator = project and project.creator_id == user_id
    if is_target_creator:
        raise HTTPException(
            403, "Cannot remove project creator. Creator always remains as manager.")

    # Proceed with soft delete
    db_member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.is_deleted == False
    ).first()

    if db_member:
        db_member.is_deleted = True
        db_member.deleted_at = datetime.utcnow()
        db.commit()
        return True
    return False


def check_project_permission(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, required_role: ProjectRole = ProjectRole.MEMBER):
    """Check if user has required permission in project"""
    member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_id,
        models.ProjectMember.role >= required_role
    ).first()

    return member is not None


def get_project_members(db: Session, project_id: uuid.UUID):
    """Get all active members of a project"""
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.is_deleted == False
    ).all()


def soft_delete_project(db: Session, project_id: uuid.UUID):
    """Soft delete project"""
    db_project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if db_project:
        db_project.is_deleted = True
        db_project.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False
