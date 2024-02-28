from datetime import datetime
from typing import Sequence
from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo


# 회원 정보 가져오기
class UserListResponse(BaseModel):
    class _User(BaseModel):
        id: int
        username: str
        email: EmailStr
        created_at: datetime
        is_admin: bool
        is_active: bool

    data: Sequence[_User]


# 회원가입
class UserCreate(BaseModel):
    password: str
    password_check: str
    username: str
    email: EmailStr

    @field_validator("password", "password_check", "username", "email")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    @field_validator("password_check")
    def passwords_match(cls, v, info: FieldValidationInfo):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return v


# OAuth 토큰 로그인
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class User(BaseModel):
    id: int
    username: str
    email: str
