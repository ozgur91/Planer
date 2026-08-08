from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from app.modules.organization.domain.exceptions import InvalidDepartmentNameError


@dataclass(slots=True)
class Department:
    MAX_NAME_LENGTH: ClassVar[int] = 100

    id: UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        self.name = self.normalize_name(self.name)
        self.description = self.normalize_description(self.description)

    def rename(self, name: str, *, changed_at: datetime) -> None:
        self.name = self.normalize_name(name)
        self.updated_at = changed_at

    def change_description(
        self,
        description: str | None,
        *,
        changed_at: datetime,
    ) -> None:
        self.description = self.normalize_description(description)
        self.updated_at = changed_at

    def deactivate(self, *, changed_at: datetime) -> None:
        self.is_active = False
        self.updated_at = changed_at

    @classmethod
    def normalize_name(cls, name: str) -> str:
        normalized_name = name.strip()

        if not normalized_name:
            raise InvalidDepartmentNameError("name must not be empty")

        if len(normalized_name) > cls.MAX_NAME_LENGTH:
            raise InvalidDepartmentNameError(
                f"name must not exceed {cls.MAX_NAME_LENGTH} characters"
            )

        return normalized_name

    @staticmethod
    def normalize_description(description: str | None) -> str | None:
        if description is None:
            return None

        normalized_description = description.strip()
        return normalized_description or None
