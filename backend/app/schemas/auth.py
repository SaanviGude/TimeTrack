# Login, Signup, Token schemas
# backend/app/schemas/auth.py

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
    sub: str | None = None # User ID (UUID as string) for JWT