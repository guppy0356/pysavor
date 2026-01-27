from sqlmodel import Session

from src import security
from src.domain.interfaces.user_repository import UserRepositoryProtocol

from .exceptions import AuthenticationError


class AuthUseCase:
    def __init__(self, session: Session, user_repository: UserRepositoryProtocol):
        self.session = session
        self.user_repository = user_repository

    def login(self, *, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email=email)
        if not user:
            raise AuthenticationError("Incorrect email or password")

        if not security.verify_password(password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")

        access_token = security.create_access_token(subject=user.id)

        return access_token
