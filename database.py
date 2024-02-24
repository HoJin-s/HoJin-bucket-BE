from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./hojin_project.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


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
