from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User

from datetime import datetime

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 회원가입
def create_user(db: Session, user_create: UserCreate):
    db_user = User(
        password=pwd_context.hash(user_create.password),
        username=user_create.username,
        email=user_create.email,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(db_user)
    db.commit()


# OAuth 토큰 로그인
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
