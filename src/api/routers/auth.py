from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session

from src.api import deps
from src.schemas import auth as auth_schema
from src.use_cases import auth as auth_use_case
from src.use_cases.exceptions import AuthenticationError
from src.repositories.user import UserRepository
from src.settings import settings

router = APIRouter()


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
        )

