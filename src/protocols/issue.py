from typing import Any, Protocol, Sequence
from sqlmodel import Session

from src.models.issue import Issue
from src.models.user import User
from src.schemas.issue import IssueCreate


class IssueRepositoryProtocol(Protocol):
    def get_by_id(self, session: Session, *, id: int) -> Issue | None:
        ...

    def find_by_scope(self, session: Session, *, scope: Any) -> Sequence[Issue]:
        ...

    def create(self, session: Session, *, issue_create: IssueCreate, owner_id: int) -> Issue:
        ...

    def add_collaborator(self, session: Session, *, issue: Issue, user: User) -> None:
        ...

