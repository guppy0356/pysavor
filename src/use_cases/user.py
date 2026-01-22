from sqlmodel import Session

from src import security
from src.models.user import User
from src.protocols.user import UserRepositoryProtocol
from src.schemas.user import UserCreate

from .exceptions import UserAlreadyExistsError


class UserUseCase:
    def __init__(self, session: Session, user_repository: UserRepositoryProtocol):
        self.session = session
        self.user_repository = user_repository

    def create_user(self, user_create: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(session=self.session, email=user_create.email)
        if existing_user:
            raise UserAlreadyExistsError("User with this email already exists.")

        hashed_password = security.get_password_hash(user_create.password)

        new_user = self.user_repository.create(
            session=self.session, user_create=user_create, hashed_password=hashed_password
        )

        self.session.commit()
        self.session.refresh(new_user)

        return new_user

