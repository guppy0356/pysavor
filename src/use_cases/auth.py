from sqlmodel import Session

from src import security
from src.protocols.user import UserRepositoryProtocol
from .exceptions import AuthenticationError


def login(
    session: Session,
    *,
    user_repository: UserRepositoryProtocol,
    email: str,
    password: str,
) -> str:
    user = user_repository.get_by_email(session=session, email=email)
    if not user:
        raise AuthenticationError("Incorrect email or password")

    if not security.verify_password(password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")

    access_token = security.create_access_token(subject=user.id)
    
    return access_token
