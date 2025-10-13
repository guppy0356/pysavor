from typing import Optional

from sqlmodel import Field, SQLModel


class Collaborator(SQLModel, table=True):
    __tablename__ = "collaborators"

    issue_id: Optional[int] = Field(
        default=None, foreign_key="issues.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
