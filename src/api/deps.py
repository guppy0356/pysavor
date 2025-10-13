from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlmodel import Session

from src.db import current_session
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.token import TokenPayload
from src.settings import settings


def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("access_token")


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
