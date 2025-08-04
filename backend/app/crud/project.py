# Project CRUD operations
from sqlalchemy.orm import Session
from .. import models
from ..schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectMemberCreate,
    ProjectMemberUpdate, ProjectRole, ProjectStatus
)
import uuid
from datetime import datetime


def create_project(db: Session, project: ProjectCreate, creator_id: uuid.UUID):
    """Create new project within workspace"""
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

    # Add creator as MANAGER
    db_member = models.ProjectMember(
        project_id=db_project.id,
        user_id=creator_id,
        role=ProjectRole.MANAGER
    )
    db.add(db_member)
    db.commit()

    return db_project


def get_workspace_projects(db: Session, workspace_id: uuid.UUID):
    """Get all projects in a workspace"""
    return db.query(models.Project).filter(
        models.Project.workspace_id == workspace_id,
        models.Project.is_deleted == False
    ).all()


def get_user_projects(db: Session, user_id: uuid.UUID):
    """Get all projects where user is a member"""
    return db.query(models.Project).join(models.ProjectMember).filter(
        models.ProjectMember.user_id == user_id,
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
    """Add member to project"""
    db_member = models.ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_project_member_role(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, role: ProjectRole):
    """Update member role in project"""
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


def remove_project_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID):
    """Remove member from project"""
    db_member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_id
    ).first()

    if db_member:
        db.delete(db_member)
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
    """Get all members of a project"""
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id
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
