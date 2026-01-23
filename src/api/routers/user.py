from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_user_use_case
from src.schemas.user import UserCreate, UserRead
from src.use_cases.exceptions import UserAlreadyExistsError
from src.use_cases.user import CreateUserCommand, UserUseCase

router = APIRouter()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user(
    *,
    user_create: UserCreate,
    use_case: UserUseCase = Depends(get_user_use_case),
) -> UserRead:
    try:
        # PydanticモデルからCommandに変換（CQRSパターン）
        command = CreateUserCommand(
            email=user_create.email,
            password=user_create.password,
            full_name=user_create.full_name,
        )
        created_user = use_case.create_user(command=command)
        return created_user

    except UserAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from err
