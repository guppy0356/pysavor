from typing import Protocol

from sqlmodel import Session

from src.adapters.db.models.user import User


class UserRepositoryProtocol(Protocol):
    def get_by_id(self, session: Session, *, id: int) -> User | None:
        ...

    def get_by_email(self, session: Session, *, email: str) -> User | None:
        ...

    def create(
        self,
        session: Session,
        *,
        email: str,
        full_name: str | None,
        hashed_password: str,
    ) -> User:
        ...
