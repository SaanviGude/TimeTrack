# Common base schemas
# backend/app/schemas/base.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# Pydantic V2 compatibility: from_attributes replaces orm_mode
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Schema for IDs (UUID)
class IDSchema(BaseSchema):
    id: uuid.UUID

# Schema for common timestamps
class TimeStampSchema(BaseSchema):
    created_at: datetime = Field(..., description="Timestamp of creation (UTC)")
    updated_at: datetime = Field(..., description="Timestamp of last update (UTC)")

# Base schema for database entities with ID and timestamps, and soft delete
class BaseDBSchema(IDSchema, TimeStampSchema):
    is_deleted: bool = Field(False, description="Flag indicating if the record is soft-deleted")