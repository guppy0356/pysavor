from dataclasses import dataclass
from sqlmodel import Session

from src import security
from src.models.user import User
from src.protocols.user import UserRepositoryProtocol

from .exceptions import UserAlreadyExistsError


@dataclass
class SignupInputData:
    email: str
    password: str
    full_name: str | None = None


class UserUseCase:
    def __init__(self, session: Session, user_repository: UserRepositoryProtocol):
        self.session = session
        self.user_repository = user_repository

    def signup(self, input_data: SignupInputData) -> User:
        existing_user = self.user_repository.get_by_email(session=self.session, email=input_data.email)
        if existing_user:
            raise UserAlreadyExistsError("User with this email already exists.")

        hashed_password = security.get_password_hash(input_data.password)

        new_user = self.user_repository.create(
            session=self.session,
            email=input_data.email,
            full_name=input_data.full_name,
            hashed_password=hashed_password,
        )

        self.session.commit()
        self.session.refresh(new_user)

        return new_user

