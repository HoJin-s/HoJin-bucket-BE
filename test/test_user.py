from typing import Sequence
from sqlalchemy import select
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from main import app
from datetime import timedelta, datetime
from jose import jwt
from dotenv import load_dotenv
import os

# 로그인 테스트 시, 사용
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

client = TestClient(app)


# 유저 없을 때 GET 테스트
@pytest.mark.asyncio
async def test_read_user_list_empty() -> None:
    response = client.get("/api/user")

    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    assert len(response.json()["data"]) == 0


# 유저 1명 GET 테스트
@pytest.mark.asyncio
async def test_read_user_list_with_one_user(one_test_user: User) -> None:
    response = client.get("/api/user")

    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["email"] == one_test_user.email
    print(response.json()["data"])


# 유저 50명 GET 테스트
@pytest.mark.asyncio
async def test_read_user_list_with_fifty_users(
    fifty_test_users: Sequence[User],
) -> None:
    response = client.get("/api/user")

    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    assert len(response.json()["data"]) == 50
    assert response.json()["data"][0]["email"] == fifty_test_users[0].email
    assert response.json()["data"][49]["email"] == fifty_test_users[49].email


# 회원가입 POST 유저정보 테스트
@pytest.mark.asyncio
async def test_user_register_success_adds_to_db(test_session: AsyncSession) -> None:
    response = client.post(
        url="/api/user/create",
        json={
            "email": "leekh9997@naver.com",
            "username": "이기호",
            "password": "password",
            "password_check": "password",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    results = await test_session.execute(select(User))
    users = results.scalars().all()

    assert len(users) == 1
    assert users[0].email == "leekh9997@naver.com"
    assert users[0].username == "이기호"


# 회원가입 POST 시, 빈값 입력
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "email": "",  # email 빈값
            "username": "이기호",
            "password": "password",
            "password_check": "password",
        },
        {
            "email": "leekh9997@naver.com",
            "username": "",  # username 빈값
            "password": "password",
            "password_check": "password",
        },
        {
            "email": "leekh9997@naver.com",
            "username": "이기호",
            "password": "",  # password 빈값
            "password_check": "password",
        },
        {
            "email": "leekh9997@naver.com",
            "username": "이기호",
            "password": "password",
            "password_check": "",  # password_check 빈값
        },
    ],
)
async def test_register_user_with_empty_fields(invalid_data: dict[str, str]) -> None:
    response = client.post(
        url="/api/user/create",
        json=invalid_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# 회원가입 POST 시, 패스워드 불일치
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "email": "leekh9997@naver.com",
            "username": "이기호",
            "password": "password",
            "password_check": "different_password",  # password_check 불일치
        },
    ],
)
async def test_register_user_with_passwords_mismatch(
    invalid_data: dict[str, str]
) -> None:
    response = client.post(
        url="/api/user/create",
        json=invalid_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# 회원가입 POST 시, email 중복
@pytest.mark.asyncio
async def test_register_user_with_duplicated_email(one_test_user: User) -> None:
    response = client.post(
        url="/api/user/create",
        json={
            "email": one_test_user.email,
            "username": "이기호",
            "password": "password",
            "password_check": "password",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT


# 회원가입 POST 시, username 중복
@pytest.mark.asyncio
async def test_register_user_with_duplicated_username(one_test_user: User) -> None:
    response = client.post(
        url="/api/user/create",
        json={
            "email": "leekh9997@naver.com",
            "username": one_test_user.username,
            "password": "password",
            "password_check": "password",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT


# 회원가입 POST 시, 비밀번호가 암호화되어 저장되는지 검증
@pytest.mark.asyncio
async def test_password_is_hashed(test_session: AsyncSession) -> None:
    response = client.post(
        url="/api/user/create",
        json={
            "email": "leekh9997@naver.com",
            "username": "이기호",
            "password": "password",
            "password_check": "password",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    results = await test_session.execute(select(User))
    users = results.scalars().all()
    assert users[0].password != "password"


# 로그인 POST 유저정보 테스트
@pytest.mark.asyncio
async def test_user_login_success(
    one_test_user: User,
) -> None:
    response = client.post(
        url="/api/user/login",
        data={
            "username": one_test_user.username,
            "password": "one_test_user",
        },
    )

    access_token_data = {
        "sub": one_test_user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(access_token_data, SECRET_KEY, algorithm=ALGORITHM)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert "username" in response.json()
    assert response.json()["access_token"] == access_token
    assert response.json()["token_type"] == "bearer"
    assert response.json()["username"] == one_test_user.username


# 로그인 POST 시, username 체크
@pytest.mark.asyncio
async def test_user_login_failure_username_dismatch(
    one_test_user: User,
) -> None:
    response = client.post(
        url="/api/user/login",
        data={
            "username": f"wrong_{one_test_user.username}",  # username 없을 때
            "password": "one_test_user",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 로그인 POST 시, password 체크
@pytest.mark.asyncio
async def test_user_login_failure_password_dismatch(
    one_test_user: User,
) -> None:
    response = client.post(
        url="/api/user/login",
        data={
            "username": one_test_user.username,
            "password": "wrong_password",  # password 불일치
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
