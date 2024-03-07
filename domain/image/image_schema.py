from pydantic import BaseModel


# 이미지 가져오기
class Image(BaseModel):
    id: int
    data: str
    bucketlist_id: int | None = None
    review_id: int | None = None


# 이미지 생성
class ImageCreate(BaseModel):
    data: str
    bucketlist_id: int | None = None
    review_id: int | None = None
