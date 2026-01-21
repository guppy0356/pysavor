from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .collaborator import Collaborator

if TYPE_CHECKING:
    from .issue import Issue


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    full_name: str | None = Field(default=None, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    issues: list["Issue"] = Relationship(back_populates="owner")

    collaborated_issues: list["Issue"] = Relationship(
        back_populates="collaborators", link_model=Collaborator
    )
