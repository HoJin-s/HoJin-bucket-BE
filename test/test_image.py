import pytest
from fastapi.testclient import TestClient
from fastapi import status, UploadFile
from models import User, BucketList, Review, Image
from main import app

client = TestClient(app)


# 특정 이미지 GET 성공
@pytest.mark.asyncio
async def test_get_image(one_test_image: Image):
    response = client.get(
        url=f"/api/image/detail/{one_test_image.id}",
    )
    assert response.json()["id"] == 1
    assert response.json()["data"] == one_test_image.data
    assert response.json()["bucketlist_id"] == one_test_image.bucketlist_id
    assert response.json()["review_id"] == None


# 특정 이미지 GET 실패
@pytest.mark.asyncio
async def test_get_image_wrong_image_id(one_test_image: Image):
    response = client.get(
        url=f"/api/image/detail/{one_test_image.id + 1}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "해당 이미지를 찾을 수 없습니다."


# 이미지 생성 POST 성공 (bucketlist 이미지)
@pytest.mark.asyncio
async def test_create_image_with_bucketlst_id(
    test_login_and_get_token,
    one_test_bucketlist: BucketList,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        params={"bucketlist_id": one_test_bucketlist.id},
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["bucketlist_id"] == 1
    assert response.json()["review_id"] == None


# 이미지 생성 POST 성공 (review 이미지)
@pytest.mark.asyncio
async def test_create_image_with_review_id(
    test_login_and_get_token,
    one_test_review: Review,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        params={"review_id": one_test_review.id},
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["bucketlist_id"] == None
    assert response.json()["review_id"] == 1


# 이미지 생성 POST 실패 (없는 버킷리스트)
@pytest.mark.asyncio
async def test_create_image_with_no_bucketlist_id(
    test_login_and_get_token,
    one_test_bucketlist: BucketList,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        params={"bucketlist_id": one_test_bucketlist.id + 1},
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "해당 버킷리스트를 찾을 수 없습니다."


# 이미지 생성 POST 실패 (없는 리뷰)
@pytest.mark.asyncio
async def test_create_image_with_no_review_id(
    test_login_and_get_token,
    one_test_review: Review,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        params={"review_id": one_test_review.id + 1},
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "해당 리뷰를 찾을 수 없습니다."


# 이미지 생성 POST 실패 (Token 미입력/미일치)
@pytest.mark.asyncio
async def test_create_image_with_unauthorized(
    test_login_and_get_token,
    one_test_bucketlist: BucketList,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer wrong_{test_login_and_get_token}"},
        params={"bucketlist_id": one_test_bucketlist.id},
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 이미지 생성 POST 실패 (bucketlist_id, review_id 둘 다 미입력시)
@pytest.mark.asyncio
async def test_create_image_with_no_id(
    test_login_and_get_token,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert (
        response.json()["detail"]
        == "bucketlist_id와 review_id 둘 중 하나를 선택하세요."
    )


# 이미지 생성 POST 실패 (bucketlist_id, review_id 둘 다 입력시)
@pytest.mark.asyncio
async def test_create_image_with_both_id(
    test_login_and_get_token,
    one_test_bucketlist: BucketList,
    one_test_review: Review,
    image_file: UploadFile,
) -> None:
    response = client.post(
        url="/api/image/create",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
        params={
            "bucketlist_id": one_test_bucketlist.id,
            "review_id": one_test_review.id,
        },
        files={
            "file": f"file:///{image_file}",
        },
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert (
        response.json()["detail"]
        == "bucketlist_id와 review_id를 모두 입력할 수 없습니다."
    )


# 이미지 삭제 DELETE 성공
@pytest.mark.asyncio
async def test_delete_image(
    test_login_and_get_token,
    one_test_image: Image,
) -> None:
    print(one_test_image)
    response = client.delete(
        url=f"/api/image/delete/{one_test_image.id}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


# 이미지 삭제 DELETE 실패 (잘못된 image_id)
@pytest.mark.asyncio
async def test_delete_image_wrong_image_id(
    test_login_and_get_token,
    one_test_image: Image,
) -> None:
    print(one_test_image)
    response = client.delete(
        url=f"/api/image/delete/{one_test_image.id + 1}",
        headers={"Authorization": f"Bearer {test_login_and_get_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "해당 이미지를 찾을 수 없습니다."


# 이미지 삭제 DELETE 실패 (Token 미입력/미일치)
@pytest.mark.asyncio
async def test_delete_image_unauthorized(
    test_login_and_get_token,
    one_test_image: Image,
) -> None:
    print(one_test_image)
    response = client.delete(
        url=f"/api/image/delete/{one_test_image.id}",
        headers={"Authorization": f"Bearer wrong_{test_login_and_get_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
