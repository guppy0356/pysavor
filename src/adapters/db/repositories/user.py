from sqlmodel import Session, select

from src.adapters.db.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, *, id: int) -> User | None:
        return self.session.get(User, id)

    def get_by_email(self, *, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()

    def add(self, user: User) -> None:
        self.session.add(user)
