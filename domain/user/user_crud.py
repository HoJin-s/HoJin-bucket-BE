from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select
from domain.user.user_schema import UserCreate
from models import User

from datetime import datetime

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 회원가입
async def create_user(db: Session, user_create: UserCreate):
    db_user = User(
        password=pwd_context.hash(user_create.password),
        username=user_create.username,
        email=user_create.email,
        created_at=datetime.now(),
    )
    db.add(db_user)
    await db.commit()


# 회원가입 확인
async def get_existing_user(db: Session, user_create: UserCreate):
    result = await db.execute(
        select(User).filter(
            (User.username == user_create.username) | (User.email == user_create.email)
        )
    )
    return result.scalars().all()


# OAuth 토큰 로그인
async def get_user(db: Session, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one()
