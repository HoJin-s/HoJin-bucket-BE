from fastapi.testclient import TestClient
from fastapi import status
from main import app

client = TestClient(app)


def test_read_user_list() -> None:
    response = client.get("/api/user")
    assert response.status_code == status.HTTP_200_OK
