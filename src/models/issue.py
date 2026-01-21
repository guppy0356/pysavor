from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel
from .collaborator import Collaborator

if TYPE_CHECKING:
    from .user import User


class Issue(SQLModel, table=True):
    __tablename__ = "issues"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="users.id")

    owner: "User" = Relationship(back_populates="issues")

    collaborators: List["User"] = Relationship(
        back_populates="collaborated_issues", link_model=Collaborator
    )

    def add_collaborator(self, user: "User") -> None:
        """Add a collaborator to this issue (domain logic)
        
        Args:
            user: User to add as a collaborator
            
        Raises:
            ValueError: If attempting to add the owner as a collaborator
        """
        # Owner cannot be added as a collaborator
        if user.id == self.owner_id:
            raise ValueError("Owner cannot be added as a collaborator")
        
        # Skip if already a collaborator
        if user in self.collaborators:
            return
        
        # Add collaborator
        self.collaborators.append(user)
