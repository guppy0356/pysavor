
from pydantic import BaseModel


class IssueBase(BaseModel):
    title: str
    description: str | None = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
