# User model
# backend/app/models/user.py

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users" # Table name in the database

    # Frontend Input: Fullname, Email, Password
    # Storing Fullname directly, or you could parse into first/last in service layer.
    full_name = Column(String, nullable=False, comment="Full name of the user")
    email = Column(String, unique=True, index=True, nullable=False, comment="User's unique email address")
    hashed_password = Column(String, nullable=False, comment="Hashed password for security")
    is_active = Column(Boolean, default=True, nullable=False, comment="Account active status")
    is_superuser = Column(Boolean, default=False, nullable=False, comment="Admin privilege status")

    # Relationships
    organization_memberships = relationship("OrganizationMember", back_populates="user")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user")
    project_memberships = relationship("ProjectMember", back_populates="user")