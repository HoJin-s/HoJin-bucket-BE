from typing import AsyncGenerator, Sequence
from datetime import datetime

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, BucketList, Review
from database import async_engine, Base, AsyncSessionLocal


@pytest_asyncio.fixture(autouse=True)
async def create_tables() -> AsyncGenerator[None, None]:
    """테스트 전 테이블 create / 테스트 후 테이블 drop"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """테스트를 위한 데이터베이스 세션 생성"""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


# 유저 1명 GET 테스트
@pytest_asyncio.fixture
async def one_test_user(test_session: AsyncSession) -> User:
    test_user = User(
        email="twicegoddessana1229@gmail.com",
        username="twicegoddessana1229",
        password="twicegoddessana1229",
        created_at=datetime.now(),
    )
    test_session.add(test_user)
    await test_session.commit()
    return test_user


# 유저 50명 GET 테스트
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
