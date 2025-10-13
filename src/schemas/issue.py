from typing import Optional

from pydantic import BaseModel

from .user import UserRead


class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None


class IssueCreate(IssueBase):
    pass


class IssueRead(IssueBase):
    id: int
    owner_id: int
    owner: UserRead


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
