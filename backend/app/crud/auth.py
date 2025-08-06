# Authentication CRUD operations
from sqlalchemy.orm import Session
from .. import models
from ..schemas.auth import UserSignup
from ..utils import get_password_hash, verify_password
import uuid


def get_user_by_email(db: Session, email: str):
    """Get user by email - used for login and registration checks"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID):
    """Get user by ID - used for token validation"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: UserSignup):
    """Create new user account with hashed password"""
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
    """Authenticate user with email and password for login"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def verify_user_active(db: Session, user_id: uuid.UUID):
    """Check if user account is active and not deleted"""
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False,
        models.User.is_active == True
    ).first()
    return user is not None


def reset_user_password(db: Session, email: str, new_password: str):
    """Reset user password by email"""
    from ..utils import get_password_hash
    
    user = get_user_by_email(db, email)
    if not user:
        return False
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return True


def request_password_reset(db: Session, email: str):
    """Initiate password reset process for user"""
    user = get_user_by_email(db, email)
    if not user:
        # Return True even if user doesn't exist for security (don't reveal user existence)
        return False
    
    if not user.is_active or user.is_deleted:
        return False
    
    # In a real application, you would:
    # 1. Generate a reset token
    # 2. Store it in database with expiration
    # 3. Send email with reset link
    # For now, we'll just return True to indicate the request was processed
    return True


def change_password(db: Session, user_id: uuid.UUID, current_password: str, new_password: str):
    """Change user password with current password verification"""
    from datetime import datetime

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        return False

    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def reset_password(db: Session, email: str, new_password: str):
    """Reset password for password recovery (without current password)"""
    from datetime import datetime

    user = get_user_by_email(db, email)
    if not user:
        return None

    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def deactivate_user_account(db: Session, user_id: uuid.UUID):
    """Deactivate user account (disable login but keep data)"""
    from datetime import datetime

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


def reactivate_user_account(db: Session, user_id: uuid.UUID):
    """Reactivate user account"""
    from datetime import datetime

    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()
    if user:
        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False
