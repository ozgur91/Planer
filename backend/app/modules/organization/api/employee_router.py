from uuid import UUID

from fastapi import APIRouter, status

from app.modules.organization.api.dependencies import EmployeeServiceDependency
from app.modules.organization.api.schemas import (
    EmployeeCreateRequest,
    EmployeeResponse,
    WorkScheduleResponse,
)

router = APIRouter(tags=["Employees"])


@router.post(
    "/teams/{team_id}/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    team_id: UUID,
    request: EmployeeCreateRequest,
    service: EmployeeServiceDependency,
) -> EmployeeResponse:
    employee = service.create_employee(
        team_id=team_id,
        personnel_number=request.personnel_number,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        entry_date=request.entry_date,
        exit_date=request.exit_date,
        work_schedule=request.work_schedule.to_domain(),
    )
    return EmployeeResponse.model_validate(employee)


@router.get(
    "/teams/{team_id}/employees",
    response_model=list[EmployeeResponse],
)
def list_employees(
    team_id: UUID,
    service: EmployeeServiceDependency,
) -> list[EmployeeResponse]:
    employees = service.list_employees(team_id)

    return [EmployeeResponse.model_validate(employee) for employee in employees]


@router.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: UUID,
    service: EmployeeServiceDependency,
) -> EmployeeResponse:
    employee = service.get_employee(employee_id)
    return EmployeeResponse.model_validate(employee)


@router.get(
    "/employees/{employee_id}/work-schedule",
    response_model=WorkScheduleResponse,
)
def get_work_schedule(
    employee_id: UUID,
    service: EmployeeServiceDependency,
) -> WorkScheduleResponse:
    schedule = service.get_work_schedule(employee_id)
    return WorkScheduleResponse.from_domain(schedule)
