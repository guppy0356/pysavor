from sqlmodel import Session, create_engine

from src.settings import settings

engine = create_engine(str(settings.DATABASE_URL), connect_args={"check_same_thread": False})


def current_session():
    with Session(engine) as session:
        yield session

