from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from src.api import deps
from src.api.deps import get_user_use_case
from src.repositories.user import UserRepository
from src.schemas import auth as auth_schema
from src.schemas.user import UserCreate, UserRead
from src.settings import settings
from src.use_cases import auth as auth_use_case
from src.use_cases.exceptions import AuthenticationError, UserAlreadyExistsError
from src.use_cases.user import UserUseCase

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
def signup(
    *,
    user_create: UserCreate,
    use_case: UserUseCase = Depends(get_user_use_case),
) -> UserRead:
    try:
        created_user = use_case.signup(
            email=user_create.email,
            password=user_create.password,
            full_name=user_create.full_name,
        )
        return created_user

    except UserAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from err


@router.post("/login", tags=["Authentication"])
def login(
    login_data: auth_schema.LoginRequest,
    response: Response,
    session: Session = Depends(deps.current_session),
):
    user_repository = UserRepository()

    try:
        access_token = auth_use_case.login(
            session=session,
            user_repository=user_repository,
            email=login_data.email,
            password=login_data.password,
        )

        response.set_cookie(
            key="pysavor_access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=settings.COOKIE_SECURE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return {"message": "Successfully logged in"}

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

