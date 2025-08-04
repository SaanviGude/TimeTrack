from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserProfile, UserBasicInfo, UserProfileUpdate, UserDeleteResponse
from .auth import get_current_user
from .. import crud

router = APIRouter()


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# New protected endpoints


@router.get("/me", response_model=UserBasicInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user basic information"""
    return UserBasicInfo(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        is_active=current_user.is_active
    )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user profile"""
    user = crud.get_user_by_id_protected(db, str(current_user.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserProfile(
        id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    user_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Convert to dict and remove None values
    update_data = {k: v for k, v in user_update.dict().items()
                   if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    updated_user = crud.update_user_profile(
        db, str(current_user.id), update_data)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists or update failed"
        )

    return UserProfile(
        id=str(updated_user.id),
        full_name=updated_user.full_name,
        email=updated_user.email,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )


@router.delete("/profile", response_model=UserDeleteResponse)
async def delete_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account (soft delete)"""
    success = crud.soft_delete_user(db, str(current_user.id))

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user account"
        )

    return UserDeleteResponse(
        message="User account successfully deleted",
        deleted_at=datetime.utcnow()
    )
