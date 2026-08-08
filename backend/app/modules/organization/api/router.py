from uuid import UUID

from fastapi import APIRouter, status

from app.modules.organization.api.dependencies import DepartmentServiceDependency
from app.modules.organization.api.schemas import (
    DepartmentCreateRequest,
    DepartmentResponse,
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    request: DepartmentCreateRequest,
    service: DepartmentServiceDependency,
) -> DepartmentResponse:
    department = service.create_department(
        name=request.name,
        description=request.description,
    )
    return DepartmentResponse.model_validate(department)


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def list_departments(
    service: DepartmentServiceDependency,
) -> list[DepartmentResponse]:
    departments = service.list_departments()

    return [DepartmentResponse.model_validate(department) for department in departments]


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: UUID,
    service: DepartmentServiceDependency,
) -> DepartmentResponse:
    department = service.get_department(department_id)
    return DepartmentResponse.model_validate(department)
