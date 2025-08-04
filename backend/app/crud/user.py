# User profile management CRUD operations
from sqlalchemy.orm import Session
from .. import models
from ..schemas.user import UserUpdate
import uuid
from datetime import datetime


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get list of all users with pagination"""
    return db.query(models.User).filter(
        models.User.is_deleted == False
    ).offset(skip).limit(limit).all()


def get_user_by_id_protected(db: Session, user_id: str):
    """Get user by ID with active status check for protected endpoints"""
    return db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False,
        models.User.is_active == True
    ).first()


def get_user_profile(db: Session, user_id: uuid.UUID):
    """Get complete user profile information"""
    return db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()


def update_user_profile(db: Session, user_id: str, user_update: dict):
    """Update user profile with validation"""
    # Check if email already exists (if email is being updated)
    if 'email' in user_update:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update['email'],
            models.User.id != user_id,
            models.User.is_deleted == False
        ).first()
        if existing_user:
            return None  # Email already exists

    # Update user
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_update.items():
            if hasattr(db_user, key) and value is not None:
                setattr(db_user, key, value)

        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user


def update_user_with_schema(db: Session, user_id: uuid.UUID, user_update: UserUpdate):
    """Update user profile using Pydantic schema"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    # Check if email already exists (if email is being updated)
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != user_id,
            models.User.is_deleted == False
        ).first()
        if existing_user:
            return None  # Email already exists

    # Update fields from schema
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_user, key) and key != 'password':  # Password handled separately
            setattr(db_user, key, value)

    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_statistics(db: Session, user_id: uuid.UUID):
    """Get user statistics (workspaces, projects, tasks counts)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    # Count owned workspaces
    owned_workspaces = db.query(models.Workspace).filter(
        models.Workspace.owner_id == user_id,
        models.Workspace.is_deleted == False
    ).count()

    # Count workspace memberships
    workspace_memberships = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.user_id == user_id
    ).count()

    # Count project memberships
    project_memberships = db.query(models.ProjectMember).filter(
        models.ProjectMember.user_id == user_id
    ).count()

    # Count assigned tasks
    assigned_tasks = db.query(models.Task).filter(
        models.Task.assigned_to_id == user_id,
        models.Task.is_deleted == False
    ).count()

    return {
        "owned_workspaces": owned_workspaces,
        "workspace_memberships": workspace_memberships,
        "project_memberships": project_memberships,
        "assigned_tasks": assigned_tasks
    }


def search_users(db: Session, query: str, limit: int = 10):
    """Search users by name or email"""
    search_pattern = f"%{query}%"
    return db.query(models.User).filter(
        models.User.is_deleted == False,
        models.User.is_active == True,
        (models.User.full_name.ilike(search_pattern) |
         models.User.email.ilike(search_pattern))
    ).limit(limit).all()


def soft_delete_user(db: Session, user_id: str):
    """Soft delete user by setting is_deleted flag"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.is_deleted = True
        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


def restore_user(db: Session, user_id: uuid.UUID):
    """Restore soft-deleted user"""
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == True
    ).first()
    if db_user:
        db_user.is_deleted = False
        db_user.is_active = True
        db_user.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


def check_email_availability(db: Session, email: str, exclude_user_id: uuid.UUID = None):
    """Check if email is available for registration or update"""
    query = db.query(models.User).filter(
        models.User.email == email,
        models.User.is_deleted == False
    )

    if exclude_user_id:
        query = query.filter(models.User.id != exclude_user_id)

    existing_user = query.first()
    return existing_user is None
