from sqlmodel import Session

from src.models.user import User
from src.schemas.user import UserCreate


class UserRepository:
    def get_by_email(self, session: Session, *, email: str) -> User | None:
        return session.query(User).filter(User.email == email).first()

    def create(self, session: Session, *, user_create: UserCreate, hashed_password: str) -> User:
        user_data = user_create.model_dump()
        
        user_data.pop("password", None)

        new_user = User(**user_data, hashed_password=hashed_password)
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user
