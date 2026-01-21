
from pydantic import BaseModel

from .user import UserRead


class IssueBase(BaseModel):
    title: str
    description: str | None = None


class IssueCreate(IssueBase):
    pass


class IssueRead(IssueBase):
    id: int
    owner_id: int
    owner: UserRead


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
