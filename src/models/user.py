from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel
from .collaborator import Collaborator

if TYPE_CHECKING:
    from .issue import Issue


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: Optional[str] = Field(default=None, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    issues: List["Issue"] = Relationship(back_populates="owner")

    collaborated_issues: List["Issue"] = Relationship(
        back_populates="collaborators", link_model=Collaborator
    )
