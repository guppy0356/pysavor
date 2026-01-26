
from ..requests.issue import IssueBase
from .user import UserRead


class IssueRead(IssueBase):
    id: int
    owner_id: int
    owner: UserRead
