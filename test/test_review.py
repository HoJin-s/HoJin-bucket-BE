import pytest
from fastapi.testclient import TestClient
from fastapi import status
from models import User, BucketList, Review
from main import app

client = TestClient(app)


# 특정 review GET 성공
@pytest.mark.asyncio
async def test_read_review_detail_success(
    one_test_review: Review, one_test_user: User, one_test_bucketlist: BucketList
) -> None:
    response = client.get(f"/api/review/detail/{one_test_review.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["title"] == one_test_review.title
    assert response.json()["content"] == one_test_review.content
    assert response.json()["updated_at"] == one_test_review.updated_at
    assert response.json()["completed_at"] == one_test_review.completed_at
    assert response.json()["user"]["id"] == one_test_user.id
    assert response.json()["user"]["email"] == one_test_user.email
    assert response.json()["user"]["username"] == one_test_user.username
    assert response.json()["bucketlist_id"] == one_test_bucketlist.id


# 특정 review GET 실패
@pytest.mark.asyncio
async def test_read_review_detail_failure(one_test_review: Review) -> None:
    response = client.get(f"/api/review/detail/{one_test_review.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# review 생성 POST 성공
@pytest.mark.asyncio
async def test_create_review(
    test_login_and_get_token, one_test_bucketlist: BucketList
) -> None:

    response = client.post(
        url=f"/api/review/create/{one_test_bucketlist.id}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "test_review_create_title",
            "content": "test_review_create_content",
            "completed_at": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status"] == "201"
    assert response.json()["success"] == "리뷰 생성완료"


# review 생성 POST (Token 미입력/미일치)
@pytest.mark.asyncio
async def test_create_review_unauthorized(
    test_login_and_get_token, one_test_bucketlist: BucketList
) -> None:

    response = client.post(
        url=f"/api/review/create/{one_test_bucketlist.id}",
        headers={"Authorization": f"Bearer wrong{test_login_and_get_token}"},
        json={
            "title": "test_review_create_title",
            "content": "test_review_create_content",
            "completed_at": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# review 생성 POST (title 미입력시)
@pytest.mark.asyncio
async def test_create_review_with_blank_title(
    test_login_and_get_token, one_test_bucketlist: BucketList
) -> None:

    response = client.post(
        url=f"/api/review/create/{one_test_bucketlist.id}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "",
            "content": "test_review_create_content",
            "completed_at": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"] == "Value error, 빈 값은 허용되지 않습니다."
    )


# review 생성 POST (title 미입력시)
@pytest.mark.asyncio
async def test_create_review_with_no_title(
    test_login_and_get_token, one_test_bucketlist: BucketList
) -> None:

    response = client.post(
        url=f"/api/review/create/{one_test_bucketlist.id}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "content": "test_review_create_content",
            "completed_at": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"


# review 생성 POST (부적절한 날짜 입력)
@pytest.mark.asyncio
async def test_create_review_with_wrong_calender(
    test_login_and_get_token, one_test_bucketlist: BucketList
) -> None:

    response = client.post(
        url=f"/api/review/create/{one_test_bucketlist.id}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "title": "test_review_create_title",
            "completed_at": "2024-03-33",
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


# review 수정 PUT 성공
@pytest.mark.asyncio
async def test_update_review(
    one_test_review: Review,
    test_login_and_get_token,
) -> None:
    """
    review 수정 기능은 {review_id}가 추가된 것 말고는 review 생성과 에러가 같습니다.
    (title 미입력/빈값, category/calender 부적절 등)
    """
    response = client.put(
        url="/api/review/update",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "review_id": one_test_review.id,
            "title": "updated_one_test_review_title",
            "content": "updated_test_review_create_content",
            "completed_at": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "200"
    assert response.json()["success"] == "리뷰 수정완료"


# review 수정 PUT 실패 (잘못된 review_id)
@pytest.mark.asyncio
async def test_update_review_wrong_review_id(
    one_test_review: Review,
    test_login_and_get_token,
) -> None:
    response = client.put(
        url="/api/review/update",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        json={
            "review_id": one_test_review.id + 1,
            "title": "updated_one_test_review_title",
            "content": "updated_test_review_create_content",
            "completed_at": "2024-03-06",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "해당 리뷰를 찾을 수 없습니다."


# review 삭제 DELETE 성공
@pytest.mark.asyncio
async def test_delete_review(
    one_test_review: Review,
    test_login_and_get_token,
) -> None:
    response = client.delete(
        url=f"/api/review/delete/{one_test_review.id}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


# review 삭제 DELETE 실패 (없는 review_id)
@pytest.mark.asyncio
async def test_delete_review_wrong_review_id(
    one_test_review: Review,
    test_login_and_get_token,
) -> None:
    response = client.delete(
        url=f"/api/review/delete/{one_test_review.id + 1}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "해당 리뷰를 찾을 수 없습니다."


# review 삭제 DELETE 실패 (Token 미입력/미일치)
@pytest.mark.asyncio
async def test_delete_review_unauthorized(
    one_test_review: Review,
    test_login_and_get_token,
) -> None:
    response = client.delete(
        url=f"/api/review/delete/{one_test_review.id}",
        headers={"Authorization": f"Bearer wrong{test_login_and_get_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
