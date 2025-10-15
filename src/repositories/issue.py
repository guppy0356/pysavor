from typing import Any, Sequence
from sqlmodel import Session, select

from src.models.issue import Issue
from src.models.user import User
from src.schemas.issue import IssueCreate


class IssueRepository:
    def get_by_id(self, session: Session, *, id: int) -> Issue | None:
        return session.get(Issue, id)

    def find_by_scope(self, session: Session, *, scope: Any) -> Sequence[Issue]:
        statement = select(Issue).where(scope)
        results = session.exec(statement)
        return results.all()

    def create(self, session: Session, *, issue_create: IssueCreate, owner_id: int) -> Issue:
        issue_data = issue_create.model_dump()

        new_issue = Issue(**issue_data, owner_id=owner_id)

        session.add(new_issue)
        session.commit()
        session.refresh(new_issue)

        return new_issue

    def add_collaborator(self, session: Session, *, issue: Issue, user: User) -> None:
        issue.collaborators.append(user)
        session.add(issue)
        session.commit()
        session.refresh(issue)
