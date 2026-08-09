from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from datetime import date, datetime
from decimal import Decimal

from app.modules.organization.domain.employee_entities import (
    Weekday,
    WeeklyWorkSchedule,
)


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


class WorkScheduleRequest(BaseModel):
    monday: Decimal = Field(default=Decimal("0"), ge=0, le=24)
    tuesday: Decimal = Field(default=Decimal("0"), ge=0, le=24)
    wednesday: Decimal = Field(default=Decimal("0"), ge=0, le=24)
    thursday: Decimal = Field(default=Decimal("0"), ge=0, le=24)
    friday: Decimal = Field(default=Decimal("0"), ge=0, le=24)
    saturday: Decimal = Field(default=Decimal("0"), ge=0, le=24)
    sunday: Decimal = Field(default=Decimal("0"), ge=0, le=24)

    def to_domain(self) -> WeeklyWorkSchedule:
        return WeeklyWorkSchedule(
            hours_by_weekday={
                Weekday.MONDAY: self.monday,
                Weekday.TUESDAY: self.tuesday,
                Weekday.WEDNESDAY: self.wednesday,
                Weekday.THURSDAY: self.thursday,
                Weekday.FRIDAY: self.friday,
                Weekday.SATURDAY: self.saturday,
                Weekday.SUNDAY: self.sunday,
            }
        )


class WorkScheduleResponse(BaseModel):
    monday: Decimal
    tuesday: Decimal
    wednesday: Decimal
    thursday: Decimal
    friday: Decimal
    saturday: Decimal
    sunday: Decimal
    total_weekly_hours: Decimal

    @classmethod
    def from_domain(
        cls,
        schedule: WeeklyWorkSchedule,
    ) -> "WorkScheduleResponse":
        return cls(
            monday=schedule.hours_for_weekday(Weekday.MONDAY),
            tuesday=schedule.hours_for_weekday(Weekday.TUESDAY),
            wednesday=schedule.hours_for_weekday(Weekday.WEDNESDAY),
            thursday=schedule.hours_for_weekday(Weekday.THURSDAY),
            friday=schedule.hours_for_weekday(Weekday.FRIDAY),
            saturday=schedule.hours_for_weekday(Weekday.SATURDAY),
            sunday=schedule.hours_for_weekday(Weekday.SUNDAY),
            total_weekly_hours=schedule.total_weekly_hours(),
        )


class EmployeeCreateRequest(BaseModel):
    personnel_number: str | None = Field(default=None, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    entry_date: date | None = None
    exit_date: date | None = None
    work_schedule: WorkScheduleRequest


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_id: UUID
    personnel_number: str | None
    first_name: str
    last_name: str
    email: str
    entry_date: date | None
    exit_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
