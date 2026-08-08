from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class TeamUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    department_id: UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
