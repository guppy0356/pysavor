from sqlmodel import Session

from src.models.user import User


class UserRepository:
    def get_by_id(self, session: Session, *, id: int) -> User | None:
        return session.get(User, id)

    def get_by_email(self, session: Session, *, email: str) -> User | None:
        return session.query(User).filter(User.email == email).first()

    def create(
        self,
        session: Session,
        *,
        email: str,
        full_name: str | None,
        hashed_password: str,
    ) -> User:
        new_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
        )

        session.add(new_user)

        return new_user
