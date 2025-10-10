from sqlmodel import Session

from src import security
from src.models.user import User
from src.protocols.user import UserRepositoryProtocol
from src.schemas.user import UserCreate

from .exceptions import UserAlreadyExistsError


def create_user(
    session: Session,
    *,
    user_repository: UserRepositoryProtocol,
    user_create: UserCreate
) -> User:
    existing_user = user_repository.get_by_email(session=session, email=user_create.email)
    if existing_user:
        raise UserAlreadyExistsError("User with this email already exists.")

    hashed_password = security.get_password_hash(user_create.password)

    new_user = user_repository.create(
        session=session, user_create=user_create, hashed_password=hashed_password
    )

    return new_user

