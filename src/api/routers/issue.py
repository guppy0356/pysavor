from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from src.adapters.db.models.issue import Issue
from src.adapters.db.models.user import User
from src.adapters.db.repositories.issue import IssueRepository
from src.adapters.db.repositories.user import UserRepository
from src.adapters.db.session import current_session
from src.api import deps
from src.api.schemas.issue import IssueCreate, IssueRead
from src.app import issue as issue_use_case

router = APIRouter()


@router.post(
    "/",
    response_model=IssueRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Issues"],
    dependencies=[Depends(deps.can_create_issue)],
)
def create_issue(
    *,
    session: Session = Depends(current_session),
    current_user: User = Depends(deps.get_current_user),
    issue_in: IssueCreate,
):
    issue_repository = IssueRepository()
    return issue_use_case.create_issue(
        session=session, current_user=current_user, issue_repository=issue_repository, issue_create=issue_in
    )

@router.get("/me", response_model=list[IssueRead], tags=["Issues"])
def read_my_issues(
    session: Session = Depends(current_session),
    current_user: User = Depends(deps.get_current_user),
):
    issue_repository = IssueRepository()
    return issue_use_case.get_my_issues(
        session=session, current_user=current_user, issue_repository=issue_repository
    )

@router.post("/{issue_id}/collaborators/{user_id}", response_model=IssueRead, tags=["Issues"])
def add_collaborator(
    *,
    session: Session = Depends(current_session),
    issue: Issue = Depends(deps.can_add_collaborator_to_issue),
    user_id: int,
):
    user_repository = UserRepository()
    issue_repository = IssueRepository()

    user_to_add = user_repository.get_by_id(session=session, id=user_id)
    if not user_to_add:
        pass

    return issue_use_case.add_collaborator(
        session=session,
        issue_repository=issue_repository,
        issue=issue,
        user_to_add=user_to_add,
    )
