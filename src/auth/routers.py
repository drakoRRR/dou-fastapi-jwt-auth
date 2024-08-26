from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.auth.models import User
from src.auth.schemas import UserCreate, ShowUser, TokenPair, ChangePassword
from src.auth.services import _create_new_user, authenticate_user, _update_user_password
from src.exceptions import AuthFailedException, BadRequestException

from src.database import get_db
from src.auth.services import (get_current_user, create_token_pair, refresh_token_state, decode_access_token,
                               logout_func, oauth2_scheme)


auth_router = APIRouter()


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_user = await _create_new_user(body, db)
        return new_user
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database error {err}")


@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenPair)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise AuthFailedException()
    return create_token_pair(user=user)


@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenPair)
async def refresh_token(refresh: Annotated[str, None] = None):
    if not refresh:
        raise BadRequestException(detail="refresh token required")
    return refresh_token_state(token=refresh)


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    await decode_access_token(token=token, db=db)
    await logout_func(token=token, db=db)

    return {"msg": "Succesfully logout"}


@auth_router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    change_password_data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await authenticate_user(db, current_user.user_name, change_password_data.old_password)
    if not user:
        raise AuthFailedException()
    await _update_user_password(user, change_password_data, db)
    return {"msg": "Password changed successfully"}