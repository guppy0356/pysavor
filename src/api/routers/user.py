from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

import src.use_cases.user as user_use_case
from src.db import current_session
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserRead
from src.use_cases.exceptions import UserAlreadyExistsError

router = APIRouter()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user(
    *,
    session: Session = Depends(current_session),
    user_create: UserCreate,
) -> UserRead:
    try:
        user_repository = UserRepository()

        created_user = user_use_case.create_user(
            session=session, user_repository=user_repository, user_create=user_create
        )
        return created_user

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
