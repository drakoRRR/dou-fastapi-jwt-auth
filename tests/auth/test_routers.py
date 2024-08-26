import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.hashing import Hasher
from src.auth.models import TokenBlacklist, User
from tests.auth.utils import EMAIL, PASSWORD, USER_NAME, create_test_user
from tests.conftest import client, db_async_session


async def test_register(client: AsyncClient, db_async_session: AsyncSession):
    username = USER_NAME + "1"
    email = "1" + EMAIL
    response = await client.post(
        "/auth/register",
        json={
            "user_name": username,
            "email": email,
            "password": PASSWORD
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_name"] == username
    assert response.json()["email"] == email

    stmt = select(User).filter_by(user_name=username)
    result = await db_async_session.execute(stmt)
    user = result.scalar_one_or_none()

    assert user is not None
    assert user.user_name == username
    assert user.email == email


async def test_login(client: AsyncClient, db_async_session: AsyncSession):
    await create_test_user(db_async_session)
    response = await client.post(
        "/auth/login",
        data={"username": USER_NAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert "access" in response_data
    assert "refresh" in response_data
    assert response_data["token_type"] == "bearer"


async def test_bad_login(client: AsyncClient, db_async_session: AsyncSession):
    await create_test_user(db_async_session)
    response = await client.post(
        "/auth/login",
        data={"username": USER_NAME + "12", "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh(client: AsyncClient, db_async_session: AsyncSession):
    await create_test_user(db_async_session)
    response = await client.post(
        "/auth/login",
        data={"username": USER_NAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response_data = response.json()

    response = await client.post(
        "/auth/refresh",
        params={"refresh": response_data["refresh"]}
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert "access" in response_data
    assert "refresh" in response_data
    assert response_data["token_type"] == "bearer"


async def test_bad_refresh(client: AsyncClient, db_async_session: AsyncSession):
    await create_test_user(db_async_session)
    response = await client.post(
        "/auth/login",
        data={"username": USER_NAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response_data = response.json()

    response = await client.post(
        "/auth/refresh",
        params={"refresh": response_data["refresh"] + "yhdys"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_bad_refresh_blank(client: AsyncClient, db_async_session: AsyncSession):
    response = await client.post(
        "/auth/refresh",
        params={"refresh": ""}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_logout(client: AsyncClient, db_async_session: AsyncSession):
    await create_test_user(db_async_session)

    response_login = await client.post(
        "/auth/login",
        data={"username": USER_NAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {response_login.json()['access']}"}
    )

    response_data = response.json()
    assert response_data["msg"] == "Succesfully logout"

    stmt = select(TokenBlacklist).filter_by(token=response_login.json()["access"])
    result = await db_async_session.execute(stmt)
    blacklisted_token = result.scalar_one_or_none()

    assert blacklisted_token is not None
    assert blacklisted_token.token == response_login.json()["access"]


async def test_change_password(client: AsyncClient, db_async_session: AsyncSession):
    user = await create_test_user(db_async_session)
    new_password = PASSWORD + "qwerty1234"
    print("User old hashed password: ", user.hashed_password)

    response_login = await client.post(
        "/auth/login",
        data={"username": USER_NAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    response = await client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {response_login.json()['access']}"},
        json={
            "old_password": PASSWORD,
            "new_password": new_password
        }
    )

    print("User new hashed password: ", user.hashed_password)

    response_data = response.json()
    assert response_data["msg"] == "Password changed successfully"
    # assert Hasher.verify_password(new_password, user.hashed_password) is True

    response_login = await client.post(
        "/auth/login",
        data={"username": USER_NAME, "password": new_password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response_login.status_code == status.HTTP_200_OK
    assert "access" in response_login.json()