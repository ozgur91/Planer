from uuid import UUID


class OrganizationError(Exception):
    """Base exception for the organization module."""


class InvalidDepartmentNameError(OrganizationError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid department name: {reason}")
        self.reason = reason


class DepartmentNotFoundError(OrganizationError):
    def __init__(self, department_id: UUID) -> None:
        super().__init__(f"Department '{department_id}' was not found.")
        self.department_id = department_id


class DepartmentNameAlreadyExistsError(OrganizationError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Department name '{name}' already exists.")
        self.name = name


class InvalidTeamNameError(OrganizationError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid team name: {reason}")
        self.reason = reason


class TeamNotFoundError(OrganizationError):
    def __init__(self, team_id: UUID) -> None:
        super().__init__(f"Team '{team_id}' was not found.")
        self.team_id = team_id


class TeamNameAlreadyExistsError(OrganizationError):
    def __init__(self, name: str, department_id: UUID) -> None:
        super().__init__(f"Team name '{name}' already exists in department '{department_id}'.")
        self.name = name
        self.department_id = department_id


class DepartmentInactiveError(OrganizationError):
    def __init__(self, department_id: UUID) -> None:
        super().__init__(f"Department '{department_id}' is inactive.")
        self.department_id = department_id
