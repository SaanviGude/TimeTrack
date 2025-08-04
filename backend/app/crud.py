from sqlalchemy.orm import Session
from . import models
from .schemas.auth import UserSignup
from .schemas.user import UserResponse
from .utils import get_password_hash, verify_password
import uuid


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: UserSignup):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_id_protected(db: Session, user_id: str):
    """Get user by ID with active status check for protected endpoints"""
    return db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False,
        models.User.is_active == True
    ).first()


def update_user_profile(db: Session, user_id: str, user_update: dict):
    """Update user profile with validation"""
    from datetime import datetime

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


def soft_delete_user(db: Session, user_id: str):
    """Soft delete user by setting is_deleted flag"""
    from datetime import datetime

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.is_deleted = True
        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False
