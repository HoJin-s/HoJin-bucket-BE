from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from settings import get_sqlalchemy_database_url_async

# # 동기
# SQLALCHEMY_DATABASE_URL = get_sqlalchemy_database_url()
# if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(
#         SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
#     )
# else:
#     engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 비동기
SQLALCHEMY_DATABASE_URL_ASYNC = get_sqlalchemy_database_url_async()
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, autocommit=False, class_=AsyncSession, expire_on_commit=False
)

naming_convention = {
    """
    MetaData 클래스를 사용하여 데이터베이스의 프라이머리 키, 유니크 키, 인덱스 키 등의 이름 규칙을 새롭게 정의했다.
    데이터베이스에서 디폴트 값으로 명명되던 프라이머리 키, 유니크 키 등의 제약조건 이름을 수동으로 설정한 것이다.
    """
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base = declarative_base(metadata=MetaData(naming_convention=naming_convention))


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def get_async_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
