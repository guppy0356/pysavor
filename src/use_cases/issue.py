from sqlmodel import Session

from src.models.issue import Issue
from src.models.user import User
from src.protocols.issue import IssueRepositoryProtocol
from src.schemas.issue import IssueCreate
from src.policies.issue import IssuePolicy


def create_issue(
    session: Session,
    *,
    current_user: User,
    issue_repository: IssueRepositoryProtocol,
    issue_create: IssueCreate,
) -> Issue:
    return issue_repository.create(
        session=session, issue_create=issue_create, owner_id=current_user.id
    )

def add_collaborator(
    session: Session,
    *,
    issue_repository: IssueRepositoryProtocol,
    issue: Issue,
    user_to_add: User,
) -> Issue:
    issue_repository.add_collaborator(session=session, issue=issue, user=user_to_add)
    return issue

def get_my_issues(
    session: Session,
    *,
    current_user: User,
    issue_repository: IssueRepositoryProtocol,
) -> list[Issue]:
    policy = IssuePolicy(user=current_user)
    scope = policy.resolve_scope()

    return issue_repository.find_by_scope(session=session, scope=scope)
