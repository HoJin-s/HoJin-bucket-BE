"""
Pydantic은 API의 입출력 항목을 다음과 같이 정의하고 검증할수 있다.

- 입출력 항목의 갯수와 타입을 설정
- 입출력 항목의 필수값 체크
- 입출력 항목의 데이터 검증
"""

import datetime

from pydantic import BaseModel, field_validator
from sqlalchemy import text


class BucketList(BaseModel):
    id: int
    title: str
    content: str
    image: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    category: str | None = None
    is_done: bool
    calender: datetime.date | None = None


# 페이지 네이션 적용을 위한 class
class BucketListList(BaseModel):
    total: int = 0
    bucketlist_list: list[BucketList] = []


class BucketListCreate(BaseModel):
    title: str
    content: str
    image: str
    category: str

    @field_validator("title", "content", "image")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v
