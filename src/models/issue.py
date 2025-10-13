from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class Issue(SQLModel, table=True):
    __tablename__ = "issues"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="users.id")

    owner: "User" = Relationship(back_populates="issues")
