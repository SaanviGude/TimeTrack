# Login, Signup, Token schemas
# backend/app/schemas/auth.py

from typing import Optional
from pydantic import Field, EmailStr
from .base import BaseSchema

class UserSignup(BaseSchema):
    full_name: str = Field(..., min_length=1, description="Full name of the user (e.g., 'John Doe')")
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, description="User's password (min 6 characters)")

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseSchema):
    sub: Optional[str] = None # User ID (UUID as string) for JWT

class ForgotPasswordRequest(BaseSchema):
    email: EmailStr = Field(..., description="Email address to send password reset link")

class ResetPasswordRequest(BaseSchema):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")

class ForgotPasswordResponse(BaseSchema):
    message: str
    reset_token: str  # For development/testing - remove in production