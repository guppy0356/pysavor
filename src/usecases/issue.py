from sqlmodel import Session

from src.domain.models.issue import Issue
from src.domain.models.user import User
from src.api.contracts.requests.issue import IssueCreate
from src.domain.policies.issue import IssuePolicy
from src.domain.interfaces.issue_repository import IssueRepositoryProtocol


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
    """Add a collaborator to an issue"""
    # Execute business logic via domain model method
    issue.add_collaborator(user_to_add)

    # Persist via repository
    return issue_repository.save(session=session, issue=issue)

def get_my_issues(
    session: Session,
    *,
    current_user: User,
    issue_repository: IssueRepositoryProtocol,
) -> list[Issue]:
    policy = IssuePolicy(user=current_user)
    scope = policy.resolve_scope()

    return issue_repository.find_by_scope(session=session, scope=scope)
