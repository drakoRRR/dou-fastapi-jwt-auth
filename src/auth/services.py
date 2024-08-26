from jose import jwt, JWTError
import uuid

from typing import Annotated, Union, Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dals import UserDAL
from src.auth.models import User, TokenBlacklist
from src.auth.hashing import Hasher

from .schemas import ShowUser, UserCreate, TokenPair, ChangePassword
from src.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS
from src.config import SECRET_KEY
from src.database import get_db
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from src.exceptions import AuthFailedException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            user_name=body.user_name,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
        )
        return ShowUser(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            is_active=user.is_active,
        )


async def _get_user_by_email_for_auth(email: str, session: AsyncSession):
    async with session.begin():
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_email(
            email=email,
        )


async def _update_user_password(user: User, body: ChangePassword, session: AsyncSession) -> ShowUser:
    if not session.in_transaction():
        async with session.begin():
            user_dal = UserDAL(session)
            return await user_dal.update_password(
                user=user,
                new_hashed_password=Hasher.get_password_hash(body.new_password)
            )
    else:
        user_dal = UserDAL(session)
        return await user_dal.update_password(
            user=user,
            new_hashed_password=Hasher.get_password_hash(body.new_password)
        )


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user_dal = UserDAL(db)
    user = await user_dal.get_user_by_username(username)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({EXP: expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({EXP: expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def create_token_pair(user: User) -> TokenPair:
    payload = {SUB: str(user.user_id), JTI: str(uuid.uuid4()), IAT: datetime.utcnow()}

    return TokenPair(
        access=create_access_token(data={**payload}),
        refresh=create_refresh_token(data={**payload}),
    )


async def decode_access_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        black_list_token = await TokenBlacklist.find_by_id(db=db, id=payload[JTI])
        if black_list_token:
            raise JWTError("Token is blacklisted")
    except JWTError:
        raise AuthFailedException()

    return payload


def refresh_token_state(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as ex:
        raise AuthFailedException()

    return TokenPair(
        access=create_access_token(data={**payload}),
        refresh=create_refresh_token(data={**payload}),
    )


async def logout_func(token: str, db: AsyncSession):
    blacklisted_token = TokenBlacklist(token=token)
    db.add(blacklisted_token)
    await db.commit()


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    token_data = await decode_access_token(token, db=db)
    if token_data is None:
        raise AuthFailedException()
    user_dal = UserDAL(db)
    user = await user_dal.get_user_by_id(uuid.UUID(token_data[SUB]))
    if user is None:
        raise AuthFailedException()
    return user