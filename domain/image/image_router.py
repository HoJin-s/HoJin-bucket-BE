from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_async_db
from domain.image import image_schema
from models import BucketList, Image, Review
from starlette import status
import os
import uuid
from dotenv import load_dotenv

load_dotenv(override=True)
BE_URL = os.getenv("BE_URL")

router = APIRouter(
    prefix="/api/image",
)

UPLOAD_DIR = "./image_file"


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    bucketlist_id: int = None,
    review_id: int = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_async_db),
):

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    content = await file.read()
    filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경
    file_path = os.path.join(UPLOAD_DIR, filename)
    file_url = f"{BE_URL}{file_path[1:]}"

    with open(file_path, "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    if bucketlist_id is not None:
        # bucketlist_id가 유효한지 확인
        bucketlist = await db.get(BucketList, bucketlist_id)
        if not bucketlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 버킷리스트를 찾을 수 없습니다.",
            )

    if review_id is not None:
        # review_id가 유효한지 확인
        review = await db.get(Review, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 리뷰를 찾을 수 없습니다.",
            )

    if bucketlist_id is not None and review_id is not None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="bucketlist_id와 review_id를 모두 입력할 수 없습니다.",
        )

    db_image = Image(
        data=file_path[1:], bucketlist_id=bucketlist_id, review_id=review_id
    )
    db.add(db_image)
    await db.commit()

    return {"filename": filename, "file_url": file_url}
