from typing import Sequence
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from models import User, BucketList, Review
from main import app

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


# 특정 bucketlist GET 성공
@pytest.mark.asyncio
async def test_read_bucketlist_detail_success(
    one_test_bucketlist: BucketList, one_test_user: User
) -> None:
    response = client.get(f"/api/bucketlist/detail/{one_test_bucketlist.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["title"] == one_test_bucketlist.title
    assert response.json()["content"] == one_test_bucketlist.content
    assert response.json()["updated_at"] == one_test_bucketlist.updated_at
    assert response.json()["category"] == one_test_bucketlist.category
    assert response.json()["is_done"] == one_test_bucketlist.is_done
    assert response.json()["user"]["id"] == one_test_user.id
    assert response.json()["user"]["email"] == one_test_user.email
    assert response.json()["user"]["username"] == one_test_user.username


# 특정 bucketlist GET 실패
@pytest.mark.asyncio
async def test_read_bucketlist_detail_failure(one_test_bucketlist: BucketList) -> None:
    response = client.get(f"/api/bucketlist/detail/{one_test_bucketlist.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# bucketlist 생성 POST 성공
@pytest.mark.asyncio
async def test_create_bucketlist(test_login_and_get_token) -> None:

    response = client.post(
        url="/api/bucketlist/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "test_bucketlist_create_title",
            "content": "test_bucketlist_create_content",
            "category": "액티비티",
            "calender": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status"] == "201"
    assert response.json()["success"] == "버킷리스트 생성완료"


# bucketlist 생성 POST (Token 미입력/미일치)
@pytest.mark.asyncio
async def test_create_bucketlist_unauthorized(test_login_and_get_token) -> None:

    response = client.post(
        url="/api/bucketlist/create",
        headers={"Authorization": f"Bearer wrong{test_login_and_get_token}"},
        json={
            "title": "test_bucketlist_create_title",
            "content": "test_bucketlist_create_content",
            "category": "액티비티",
            "calender": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# bucketlist 생성 POST (title 미입력시)
@pytest.mark.asyncio
async def test_create_bucketlist_with_blank_title(test_login_and_get_token) -> None:

    response = client.post(
        url="/api/bucketlist/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "",
            "content": "test_bucketlist_create_content",
            "category": "액티비티",
            "calender": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"] == "Value error, 빈 값은 허용되지 않습니다."
    )


# bucketlist 생성 POST (title 미입력시)
@pytest.mark.asyncio
async def test_create_bucketlist_with_no_title(test_login_and_get_token) -> None:

    response = client.post(
        url="/api/bucketlist/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "content": "test_bucketlist_create_content",
            "category": "액티비티",
            "calender": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"


# bucketlist 생성 POST (부적절한 카테고리 입력)
@pytest.mark.asyncio
async def test_create_bucketlist_with_wrong_category(test_login_and_get_token) -> None:

    response = client.post(
        url="/api/bucketlist/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "test_bucketlist_create_title",
            "category": "없는 카테고리",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be '음식점', '카페', '체험', '액티비티', '여행', '쇼핑', '운동', '게임', '영화' or '기타'"
    )


# bucketlist 생성 POST (부적절한 날짜 입력)
@pytest.mark.asyncio
async def test_create_bucketlist_with_wrong_calender(test_login_and_get_token) -> None:

    response = client.post(
        url="/api/bucketlist/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "test_bucketlist_create_title",
            "calender": "2024-03-33",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be a valid date or datetime, day value is outside expected range"
    )
    assert (
        response.json()["detail"][0]["ctx"]["error"]
        == "day value is outside expected range"
    )


# bucketlist 수정 PUT 성공
@pytest.mark.asyncio
async def test_update_bucketlist(
    one_test_bucketlist: BucketList,
    test_login_and_get_token,
) -> None:
    """
    bucketlist 수정 기능은 {bucketlist_id}가 추가된 것 말고는 bucketlist 생성과 에러가 같습니다.
    (title 미입력/빈값, category/calender 부적절 등)
    """
    response = client.put(
        url="/api/bucketlist/update",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "bucketlist_id": one_test_bucketlist.id,
            "title": "updated_one_test_bucketlist_title",
            "content": "updated_test_bucketlist_create_content",
            "category": "액티비티",
            "calender": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "200"
    assert response.json()["success"] == "버킷리스트 수정완료"


# bucketlist 수정 PUT 실패 (잘못된 bucketlist_id)
@pytest.mark.asyncio
async def test_update_bucketlist_wrong_bucketlist_id(
    one_test_bucketlist: BucketList,
    test_login_and_get_token,
) -> None:
    response = client.put(
        url="/api/bucketlist/update",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "bucketlist_id": one_test_bucketlist.id + 1,
            "title": "updated_one_test_bucketlist_title",
            "content": "updated_test_bucketlist_create_content",
            "category": "액티비티",
            "calender": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "해당 게시글을 찾을 수 없습니다."
