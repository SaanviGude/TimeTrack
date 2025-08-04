# User specific schemas
# backend/app/schemas/user.py

import uuid
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from .base import BaseDBSchema, BaseSchema

# If storing full_name directly


class UserBase(BaseSchema):
    full_name: str
    email: EmailStr
    is_active: bool
    is_superuser: bool = False  # Default for general users


class UserResponse(UserBase):
    id: uuid.UUID  # Include ID for response


class UserUpdate(BaseSchema):
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None  # For changing password
    is_active: bool | None = None
    # is_superuser should not be updatable by regular users

# New schemas for protected user endpoints


class UserProfile(BaseSchema):
    """Complete user profile response"""
    id: str
    full_name: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBasicInfo(BaseSchema):
    """Basic user information response"""
    id: str
    full_name: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseSchema):
    """User profile update request"""
    full_name: Optional[str] = None
    email: Optional[str] = None


class UserDeleteResponse(BaseSchema):
    """User deletion response"""
    message: str
    deleted_at: datetime
