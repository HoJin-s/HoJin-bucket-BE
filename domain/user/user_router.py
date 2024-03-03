from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from database import get_db, get_async_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context

from dotenv import load_dotenv
import os

from models import User

load_dotenv(override=True)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

router = APIRouter(
    prefix="/api/user",
)


# 회원 정보 전체 가져오기
@router.get(
    "/",
    response_model=user_schema.UserListResponse,
    tags=(["User"]),
    summary=("회원 정보 전체 가져오기"),
)
async def get_users(db: Session = Depends(get_async_db)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    return {"data": users}


# 회원가입
@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    tags=(["User"]),
    summary=("회원가입"),
    description=(
        "password : 비밀번호 \n\n password_check : 비밀번호 확인 (password와 동일한 값 입력) \n\n username : 이름 (로그인 시 사용) \n\n email : 이메일 형태로 입력 "
    ),
)
async def user_create(
    _user_create: user_schema.UserCreate, db: Session = Depends(get_async_db)
):
    user = await user_crud.get_existing_user(db=db, user_create=_user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다."
        )
    await user_crud.create_user(db=db, user_create=_user_create)


# 로그인
@router.post(
    "/login",
    response_model=user_schema.Token,
    tags=(["User"]),
    summary=("로그인"),
    description=("username : 회원가입 이름 \n\n password : 회원가입 비밀번호"),
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_async_db),
):  # fastapi의 security 패키지에 있는 OAuth2PasswordRequestForm 클래스를 사용

    # 유저 / 비밀번호 체크
    user = await user_crud.get_user(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="존재하지 않는 아이디입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # access token 생성
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }


# 로그인 확인(Token 유효성 검사)
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_async_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="사용자 인증을 할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = await user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user
