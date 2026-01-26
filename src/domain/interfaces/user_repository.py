from typing import Protocol

from src.domain.models.user import User


class UserRepositoryProtocol(Protocol):
    def get_by_id(self, *, id: int) -> User | None:
        ...

    def get_by_email(self, *, email: str) -> User | None:
        ...

    def add(self, user: User) -> None:
        ...
