from uuid import UUID

from fastapi import APIRouter, Response, status

from app.modules.organization.api.dependencies import DepartmentServiceDependency
from app.modules.organization.api.schemas import (
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
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


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: UUID,
    request: DepartmentUpdateRequest,
    service: DepartmentServiceDependency,
) -> DepartmentResponse:
    department = service.update_department(
        department_id,
        name=request.name,
        description=request.description,
        description_provided="description" in request.model_fields_set,
    )
    return DepartmentResponse.model_validate(department)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_department(
    department_id: UUID,
    service: DepartmentServiceDependency,
) -> Response:
    service.deactivate_department(department_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
