from fastapi import Depends, HTTPException, Path, status, Request
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlmodel import Session

from src.db import current_session
from src.models.user import User
from src.models.issue import Issue
from src.repositories.user import UserRepository
from src.repositories.issue import IssueRepository
from src.schemas.token import TokenPayload
from src.settings import settings
from src.policies.issue import IssuePolicy


def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("pysavor_access_token")


def get_current_user(
    session: Session = Depends(current_session),
    token: str | None = Depends(get_token_from_cookie),
) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user_repository = UserRepository()

    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token payload",
        )
        
    user = user_repository.get_by_id(session, id=token_data.sub)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

def get_issue_by_id_from_path(
    issue_id: int = Path(..., gt=0),
    session: Session = Depends(current_session),
) -> Issue:
    issue_repo = IssueRepository()
    issue = issue_repo.get_by_id(session=session, id=issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue

def get_user_by_id_from_path(
    user_id: int = Path(..., gt=0, alias="user_id"),
    session: Session = Depends(current_session),
) -> User:
    """パスパラメータからuser_idを取得し、Userオブジェクトを返すDI。"""
    user_repo = UserRepository()
    user = user_repo.get_by_id(session=session, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def can_create_issue(
    current_user: User = Depends(get_current_user),
) -> None:
    policy = IssuePolicy(user=current_user)
    if not policy.can_create():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create issues",
        )

def can_update_issue(
    issue: Issue = Depends(get_issue_by_id_from_path),
    current_user: User = Depends(get_current_user),
) -> Issue:
    policy = IssuePolicy(user=current_user)
    if not policy.can_update(issue):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this issue",
        )
    return issue

def can_delete_issue(
    issue: Issue = Depends(get_issue_by_id_from_path),
    current_user: User = Depends(get_current_user),
) -> Issue:
    policy = IssuePolicy(user=current_user)
    if not policy.can_delete(issue):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this issue",
        )
    return issue

def can_add_collaborator_to_issue(
    issue: Issue = Depends(get_issue_by_id_from_path),
    user_to_add: User = Depends(get_user_by_id_from_path),
    current_user: User = Depends(get_current_user),
) -> Issue:
    policy = IssuePolicy(user=current_user)
    if not policy.can_add_collaborator(issue=issue, user_to_add=user_to_add):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add this collaborator to this issue",
        )
    return issue
