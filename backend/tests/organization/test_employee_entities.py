from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.organization.domain.employee_entities import (
    Employee,
    Weekday,
    WeeklyWorkSchedule,
)
from app.modules.organization.domain.exceptions import (
    InvalidEmployeeError,
    InvalidWorkScheduleError,
)


def create_employee(
    *,
    entry_date: date | None = None,
    exit_date: date | None = None,
) -> Employee:
    timestamp = datetime(2026, 8, 9, tzinfo=UTC)

    return Employee(
        id=uuid4(),
        team_id=uuid4(),
        personnel_number="  10042  ",
        first_name="  Erika  ",
        last_name="  Mustermann  ",
        email="  Erika.Mustermann@EXAMPLE.COM  ",
        entry_date=entry_date,
        exit_date=exit_date,
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )


def test_employee_normalizes_personal_data() -> None:
    employee = create_employee()

    assert employee.personnel_number == "10042"
    assert employee.first_name == "Erika"
    assert employee.last_name == "Mustermann"
    assert employee.email == "erika.mustermann@example.com"


def test_employee_rejects_invalid_employment_dates() -> None:
    with pytest.raises(
        InvalidEmployeeError,
        match="exit date must not be before entry date",
    ):
        create_employee(
            entry_date=date(2026, 8, 10),
            exit_date=date(2026, 8, 9),
        )


def test_work_schedule_calculates_weekly_hours() -> None:
    schedule = WeeklyWorkSchedule(
        hours_by_weekday={
            Weekday.MONDAY: Decimal("7.7"),
            Weekday.TUESDAY: Decimal("7.7"),
            Weekday.WEDNESDAY: Decimal("3.85"),
            Weekday.THURSDAY: Decimal("7.7"),
        }
    )

    assert schedule.total_weekly_hours() == Decimal("26.95")
    assert schedule.hours_for_weekday(Weekday.FRIDAY) == Decimal("0")


def test_work_schedule_calculates_person_days_for_date() -> None:
    schedule = WeeklyWorkSchedule(
        hours_by_weekday={
            Weekday.MONDAY: Decimal("7.7"),
            Weekday.TUESDAY: Decimal("3.85"),
        }
    )

    assert schedule.person_days_for_date(
        date(2026, 8, 10),
        hours_per_person_day=Decimal("7.7"),
    ) == Decimal("1")

    assert schedule.person_days_for_date(
        date(2026, 8, 11),
        hours_per_person_day=Decimal("7.7"),
    ) == Decimal("0.5")


def test_work_schedule_rejects_negative_hours() -> None:
    with pytest.raises(
        InvalidWorkScheduleError,
        match="must not be negative",
    ):
        WeeklyWorkSchedule(
            hours_by_weekday={
                Weekday.MONDAY: Decimal("-1"),
            }
        )
