from typing import Sequence
from sqlalchemy import select
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, BucketList, Review
from main import app

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

