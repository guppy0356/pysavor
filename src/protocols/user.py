from typing import Protocol
from sqlmodel import Session

from src.models.user import User
from src.schemas.user import UserCreate


class UserRepositoryProtocol(Protocol):
    def get_by_email(self, session: Session, *, email: str) -> User | None:
        ...

    def create(self, session: Session, *, user_create: UserCreate, hashed_password: str) -> User:
        ...
