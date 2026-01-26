
from sqlmodel import Field, SQLModel


class Collaborator(SQLModel, table=True):
    __tablename__ = "collaborators"

    issue_id: int | None = Field(
        default=None, foreign_key="issues.id", primary_key=True
    )
    user_id: int | None = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
