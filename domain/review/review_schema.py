"""
Pydantic은 API의 입출력 항목을 다음과 같이 정의하고 검증할수 있다.

- 입출력 항목의 갯수와 타입을 설정
- 입출력 항목의 필수값 체크
- 입출력 항목의 데이터 검증
"""

import datetime

from pydantic import BaseModel, field_validator
from domain.user.user_schema import User


# 리뷰 모델
class Review(BaseModel):
    id: int
    title: str
    content: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None
    completed_at: datetime.date | None = None
    user: User
    bucketlist_id: int


# 리뷰 생성
class ReviewCreate(BaseModel):
    title: str
    content: str | None = None
    completed_at: datetime.date | None = None

    @field_validator("title")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v


# 리뷰 수정
class ReviewUpdate(ReviewCreate):
    review_id: int


# 리뷰 삭제
class ReviewDelete(BaseModel):
    review_id: int
