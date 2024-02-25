from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./hojin_project.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
"""
MetaData 클래스를 사용하여 데이터베이스의 프라이머리 키, 유니크 키, 인덱스 키 등의 이름 규칙을 새롭게 정의했다.
데이터베이스에서 디폴트 값으로 명명되던 프라이머리 키, 유니크 키 등의 제약조건 이름을 수동으로 설정한 것이다.
"""
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base.metadata = MetaData(naming_convention=naming_convention)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    """
    with get_db() as db:
    
    db 세션 객체를 사용한다. 오류 여부에 상관없이 with문을 벗어나는 순간
    db.close()가 실행되므로 보다 안전한 코드로 변경된 것이다.
    
    Depends 함수 사용시, @contextlib.contextmanager 어노테이션을 제거하지 않으면 2중으로 적용되어 오류가 발생한다.
    """
