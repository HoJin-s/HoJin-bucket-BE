# import pytest
# from fastapi.testclient import TestClient
# from fastapi import status

# from models import User, BucketList, Review
# from main import app

# client = TestClient(app)


# # bucketlist 없을 때 GET 테스트
# @pytest.mark.asyncio
# async def test_read_bucketlist_list_empty() -> None:
#     response = client.get("/api/bucketlist/list")

#     assert response.status_code == status.HTTP_200_OK
#     assert "total" in response.json()
#     assert "bucketlist_list" in response.json()
#     assert response.json()["total"] == 0
#     assert len(response.json()["bucketlist_list"]) == 0


# # bucketlist 1개 GET 테스트
# @pytest.mark.asyncio
# async def test_read_bucketlist_with_one_bucketlist(
#     one_test_user: User, one_test_bucketlist=BucketList
# ) -> None:
#     response = client.get("/api/bucketlist/list")

#     assert response.status_code == status.HTTP_200_OK
#     assert "total" in response.json()
#     assert "bucketlist_list" in response.json()
#     assert response.json()["total"] == 1
#     assert len(response.json()["bucketlist_list"]) == 1
