# Organization and OrganizationMember models
# backend/app/models/organization.py

from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

# Define the enum locally to avoid circular imports
class OrganizationRole(IntEnum):
    OWNER = 1
    MEMBER = 2

class Organization(BaseModel):
    __tablename__ = "organizations"

    name = Column(String, index=True, nullable=False, comment="Name of the organization")
    description = Column(String, nullable=True, comment="Description of the organization")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                      comment="ID of the user who owns this organization")

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="organization", cascade="all, delete-orphan")

class OrganizationMember(BaseModel):
    __tablename__ = "organization_members"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False,
                             comment="ID of the organization")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
                     comment="ID of the user who is a member")
    role = Column(Enum(OrganizationRole, name='organization_role_enum'), default=OrganizationRole.MEMBER, nullable=False,
                  comment="Role of the user within the organization")

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")