from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from src.adapters.db.repositories.user import UserRepository
from src.adapters.db.session import current_session
from src.api import deps
from src.api.deps import get_user_use_case
from src.api.schemas import auth as auth_schema
from src.api.schemas.user import UserCreate, UserRead
from src.app import auth as auth_use_case
from src.app.exceptions import AuthenticationError, UserAlreadyExistsError
from src.app.user import UserUseCase
from src.settings import settings

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


@router.post("/signin", tags=["Authentication"])
def login(
    login_data: auth_schema.LoginRequest,
    response: Response,
    session: Session = Depends(current_session),
):
    user_repository = UserRepository(session)

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

