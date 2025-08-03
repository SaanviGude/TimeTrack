# User specific schemas
# backend/app/schemas/user.py

import uuid
from pydantic import EmailStr
from .base import BaseDBSchema, BaseSchema

# If storing full_name directly
class UserBase(BaseSchema):
    full_name: str
    email: EmailStr
    is_active: bool
    is_superuser: bool = False # Default for general users

class UserResponse(UserBase):
    id: uuid.UUID # Include ID for response

class UserUpdate(BaseSchema):
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None # For changing password
    is_active: bool | None = None
    # is_superuser should not be updatable by regular users
