from typing import AsyncGenerator, Sequence
from datetime import datetime
from passlib.context import CryptContext
import pytest_asyncio
import aiofiles
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient
from fastapi import status
from models import User, BucketList, Review
from database import Base, get_async_db
from main import app


SQLALCHEMY_DATABASE_URL_ASYNC_TEST = "sqlite+aiosqlite:///hojin_project_test.db"
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL_ASYNC_TEST, echo=False)
TestingAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """테스트를 위한 데이터베이스 세션 생성"""
    db = TestingAsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@pytest_asyncio.fixture(autouse=True)
async def create_tables() -> AsyncGenerator[None, None]:
    """테스트 전 테이블 create / 테스트 후 테이블 drop"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(autouse=True)
async def client(test_session):
    """종속성 오버라이딩"""

    async def override_get_async_db():
        try:
            yield test_session
        finally:
            await test_session.close()

    app.dependency_overrides[get_async_db] = override_get_async_db

    yield TestClient(app)


# 유저 1명 생성
@pytest_asyncio.fixture
async def one_test_user(test_session: AsyncSession) -> User:

    test_user = User(
        email="one_test_user@gmail.com",
        username="one_test_user",
        password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
            "one_test_user"
        ),
        created_at=datetime.now(),
    )
    test_session.add(test_user)
    await test_session.commit()
    return test_user


# 유저 50명 생성
@pytest_asyncio.fixture
async def fifty_test_users(test_session: AsyncSession) -> Sequence[User]:
    test_users = [
        User(
            email=f"test{i+1}@gmail.com",
            username=f"test{i+1}",
            password=f"test{i+1}",
            created_at=datetime.now(),
        )
        for i in range(50)
    ]
    test_session.add_all(test_users)
    await test_session.commit()
    return test_users


# 글 1개 생성
@pytest_asyncio.fixture
async def one_test_bucketlist(
    one_test_user: User, test_session: AsyncSession
) -> BucketList:

    one_test_bucketlist = BucketList(
        title="one_test_bucketlist_title",
        content="one_test_bucketlist_content",
        created_at=datetime.now(),
        user=one_test_user,
    )
    test_session.add(one_test_bucketlist)
    await test_session.commit()
    return one_test_bucketlist


# 글 15개 생성
@pytest_asyncio.fixture
async def fifteen_test_bucketlist(
    one_test_user: User, test_session: AsyncSession
) -> Sequence[BucketList]:
    test_bucketlists = [
        BucketList(
            title=f"test_bucketlist_title_{i+1}",
            content=f"test_bucketlist_content_{i+1}",
            created_at=datetime.now(),
            user=one_test_user,
        )
        for i in range(15)
    ]
    test_session.add_all(test_bucketlists)
    await test_session.commit()
    return test_bucketlists


# 토큰 로그인 (GET token)
@pytest_asyncio.fixture
async def test_login_and_get_token(client: TestClient, one_test_user: User) -> str:
    response = client.post(
        "/api/user/login",
        data={
            "username": one_test_user.username,
            "password": "one_test_user",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return token


# 리뷰 1개 생성
@pytest_asyncio.fixture
async def one_test_review(
    one_test_user: User, one_test_bucketlist: BucketList, test_session: AsyncSession
) -> Review:

    one_test_review = Review(
        title="one_test_review_title",
        content="one_test_review_content",
        created_at=datetime.now(),
        user=one_test_user,
        bucketlist=one_test_bucketlist,
    )
    test_session.add(one_test_review)
    await test_session.commit()
    return one_test_review


# 이미지 1개 생성
@pytest_asyncio.fixture
async def image_file(tmp_path):
    file_path = tmp_path / "test_image.jpg"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(b"image data")
    return file_path
