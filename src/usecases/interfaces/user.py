from typing import Protocol

from src.domain.models.user import User


class UserUseCaseProtocol(Protocol):
    def signup(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> User:
        ...
