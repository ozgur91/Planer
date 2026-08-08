from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import IntEnum
from typing import ClassVar
from uuid import UUID

from app.modules.organization.domain.exceptions import (
    InvalidEmployeeError,
    InvalidWorkScheduleError,
)


class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass(slots=True)
class WeeklyWorkSchedule:
    MAX_DAILY_HOURS: ClassVar[Decimal] = Decimal("24")
    ZERO_HOURS: ClassVar[Decimal] = Decimal("0")

    hours_by_weekday: dict[Weekday, Decimal]

    def __post_init__(self) -> None:
        normalized_hours: dict[Weekday, Decimal] = {}

        for weekday, hours in self.hours_by_weekday.items():
            normalized_weekday = Weekday(weekday)
            normalized_value = Decimal(str(hours))

            if normalized_value < self.ZERO_HOURS:
                raise InvalidWorkScheduleError(
                    f"hours for {normalized_weekday.name} must not be negative"
                )

            if normalized_value > self.MAX_DAILY_HOURS:
                raise InvalidWorkScheduleError(
                    f"hours for {normalized_weekday.name} must not exceed {self.MAX_DAILY_HOURS}"
                )

            normalized_hours[normalized_weekday] = normalized_value

        self.hours_by_weekday = normalized_hours

    def hours_for_weekday(self, weekday: Weekday) -> Decimal:
        return self.hours_by_weekday.get(weekday, self.ZERO_HOURS)

    def hours_for_date(self, work_date: date) -> Decimal:
        return self.hours_for_weekday(Weekday(work_date.weekday()))

    def total_weekly_hours(self) -> Decimal:
        return sum(
            self.hours_by_weekday.values(),
            start=self.ZERO_HOURS,
        )

    def person_days_for_date(
        self,
        work_date: date,
        *,
        hours_per_person_day: Decimal,
    ) -> Decimal:
        if hours_per_person_day <= self.ZERO_HOURS:
            raise InvalidWorkScheduleError("hours per person day must be greater than zero")

        return self.hours_for_date(work_date) / hours_per_person_day


@dataclass(slots=True)
class Employee:
    MAX_NAME_LENGTH: ClassVar[int] = 100
    MAX_EMAIL_LENGTH: ClassVar[int] = 254
    MAX_PERSONNEL_NUMBER_LENGTH: ClassVar[int] = 50

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

    def __post_init__(self) -> None:
        self.first_name = self.normalize_name(
            self.first_name,
            field_name="first name",
        )
        self.last_name = self.normalize_name(
            self.last_name,
            field_name="last name",
        )
        self.email = self.normalize_email(self.email)
        self.personnel_number = self.normalize_personnel_number(self.personnel_number)
        self.validate_employment_dates(
            self.entry_date,
            self.exit_date,
        )

    @classmethod
    def normalize_name(cls, name: str, *, field_name: str) -> str:
        normalized_name = name.strip()

        if not normalized_name:
            raise InvalidEmployeeError(f"{field_name} must not be empty")

        if len(normalized_name) > cls.MAX_NAME_LENGTH:
            raise InvalidEmployeeError(
                f"{field_name} must not exceed {cls.MAX_NAME_LENGTH} characters"
            )

        return normalized_name

    @classmethod
    def normalize_email(cls, email: str) -> str:
        normalized_email = email.strip().casefold()

        if (
            not normalized_email
            or "@" not in normalized_email
            or normalized_email.startswith("@")
            or normalized_email.endswith("@")
        ):
            raise InvalidEmployeeError("email address is invalid")

        if len(normalized_email) > cls.MAX_EMAIL_LENGTH:
            raise InvalidEmployeeError(f"email must not exceed {cls.MAX_EMAIL_LENGTH} characters")

        return normalized_email

    @classmethod
    def normalize_personnel_number(
        cls,
        personnel_number: str | None,
    ) -> str | None:
        if personnel_number is None:
            return None

        normalized_number = personnel_number.strip()

        if not normalized_number:
            return None

        if len(normalized_number) > cls.MAX_PERSONNEL_NUMBER_LENGTH:
            raise InvalidEmployeeError(
                f"personnel number must not exceed {cls.MAX_PERSONNEL_NUMBER_LENGTH} characters"
            )

        return normalized_number

    @staticmethod
    def validate_employment_dates(
        entry_date: date | None,
        exit_date: date | None,
    ) -> None:
        if entry_date is not None and exit_date is not None and exit_date < entry_date:
            raise InvalidEmployeeError("exit date must not be before entry date")
