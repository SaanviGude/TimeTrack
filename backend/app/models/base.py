# Base model for common fields
# backend/app/models/base.py

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID # Specific for PostgreSQL UUID type
from ..database import Base # Import the Base from your database setup

class BaseModel(Base):
    __abstract__ = True # This tells SQLAlchemy not to create a table for BaseModel itself

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True,
                comment="Unique identifier for the record (UUID)")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
                        comment="Timestamp when the record was created (UTC)")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False,
                        comment="Timestamp when the record was last updated (UTC)")
    is_deleted = Column(Boolean, default=False, nullable=False,
                        comment="Soft delete flag")