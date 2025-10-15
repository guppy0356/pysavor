from sqlalchemy import or_
from sqlmodel import Session, select

from src.models.issue import Issue
from src.models.user import User
from src.models.collaborator import Collaborator


class IssuePolicy:
    def __init__(self, user: User):
        self.user = user

    def can_create(self) -> bool:
        return self.user is not None

    def can_update(self, issue: Issue) -> bool:
        is_owner = self.user.id == issue.owner_id
        is_collaborator = self.user in issue.collaborators
        return is_owner or is_collaborator

    def can_delete(self, issue: Issue) -> bool:
        return self.user.id == issue.owner_id

    def can_add_collaborator(self, issue: Issue, user_to_add: User) -> bool:
        if self.user.id != issue.owner_id:
            return False
        
        if user_to_add.id == issue.owner_id:
            return False

        if user_to_add in issue.collaborators:
            return False
            
        return True

    def resolve_scope(self):
        return or_(
            Issue.owner_id == self.user.id,
            Issue.id.in_(
                select(Collaborator.issue_id).where(Collaborator.user_id == self.user.id)
            )
        )

