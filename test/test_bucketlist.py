from typing import Sequence
import pytest
from fastapi.testclient import TestClient
from fastapi import status, Depends
from sqlalchemy import select
from models import User, BucketList, Review
from main import app
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db

client = TestClient(app)


# bucketlist 없을 때 GET 테스트
@pytest.mark.asyncio
async def test_read_bucketlist_list_empty() -> None:
    response = client.get("/api/bucketlist/list")

    assert response.status_code == status.HTTP_200_OK
    assert "total" in response.json()
    assert "bucketlist_list" in response.json()
    assert response.json()["total"] == 0
    assert len(response.json()["bucketlist_list"]) == 0


# bucketlist 1개 GET 테스트
@pytest.mark.asyncio
async def test_read_bucketlist_with_one_bucketlist(
    one_test_bucketlist: BucketList,
    one_test_user: User,
) -> None:
    response = client.get("/api/bucketlist/list")

    assert response.status_code == status.HTTP_200_OK
    assert "total" in response.json()
    assert "bucketlist_list" in response.json()
    assert response.json()["total"] == 1
    assert len(response.json()["bucketlist_list"]) == 1
    assert response.json()["bucketlist_list"][0]["id"] == one_test_bucketlist.id
    assert response.json()["bucketlist_list"][0]["title"] == one_test_bucketlist.title
    assert (
        response.json()["bucketlist_list"][0]["content"] == one_test_bucketlist.content
    )
    assert response.json()["bucketlist_list"][0]["updated_at"] == None
    assert response.json()["bucketlist_list"][0]["category"] == None
    assert response.json()["bucketlist_list"][0]["user"]["id"] == one_test_user.id
    assert (
        response.json()["bucketlist_list"][0]["user"]["username"]
        == one_test_user.username
    )
    assert response.json()["bucketlist_list"][0]["user"]["email"] == one_test_user.email
    assert response.json()["bucketlist_list"][0]["reviews"] == []


# bucketlist 15개 GET 테스트
@pytest.mark.asyncio
async def test_read_bucketlist_with_fifteen_bucketlist(
    fifteen_test_bucketlist: Sequence[BucketList], one_test_user: User
) -> None:
    """
    비동기로 글 15개를 생성할 때, DB에 저장되는 순서가 가끔 바뀐다.
    (테스트코드 실행 시 아래의 print로 확인가능)
    """
    response = client.get("/api/bucketlist/list")
    assert response.status_code == status.HTTP_200_OK
    assert "total" in response.json()
    assert "bucketlist_list" in response.json()
    assert response.json()["total"] == 15  # 총 게시글 15개
    assert len(response.json()["bucketlist_list"]) == 10  # 1 페이지게시글 10개

    for i in range(len(response.json()["bucketlist_list"])):
        print(response.json()["bucketlist_list"][i]["title"])

        assert (
            response.json()["bucketlist_list"][i]["user"]["email"]
            == one_test_user.email
        )


# bucketlist 15개 GET 테스트 (2페이지)
@pytest.mark.asyncio
async def test_read_bucketlist_with_fifteen_bucketlist_second_page(
    fifteen_test_bucketlist: Sequence[BucketList],
) -> None:
    page = 1
    size = 10
    keyword = ""
    response = client.get(
        f"/api/bucketlist/list?page={page}&size={size}&keyword={keyword}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert "total" in response.json()
    assert "bucketlist_list" in response.json()
    assert response.json()["total"] == 15  # 총 게시글 15개
    assert len(response.json()["bucketlist_list"]) == 5  # 2 페이지게시글 5개


# bucketlist 15개 GET 테스트 (keyword 검색)
@pytest.mark.asyncio
async def test_read_bucketlist_with_fifteen_bucketlist_search(
    fifteen_test_bucketlist: Sequence[BucketList],
) -> None:
    keyword = "7"  # 7검색
    response = client.get(f"/api/bucketlist/list?&keyword={keyword}")

    assert response.status_code == status.HTTP_200_OK
    assert "total" in response.json()
    assert "bucketlist_list" in response.json()
    assert response.json()["total"] == 1  # 검색 결과 1개
    assert len(response.json()["bucketlist_list"]) == 1

