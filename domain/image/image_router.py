from fastapi import APIRouter, Body, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_async_db
from domain.image import image_crud
from models import BucketList, Review
from starlette import status
from domain.image.image_schema import ImageCreate
import os
import uuid
from dotenv import load_dotenv

load_dotenv(override=True)
BE_URL = os.getenv("BE_URL")

router = APIRouter(
    prefix="/api/image",
)

UPLOAD_DIR = "./image_file"


# 이미지 생성하기
@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=ImageCreate,
    tags=(["Image"]),
    summary=("이미지 생성"),
    description=(
        "※ bucketlist_id / review_id 둘 중 하나만 입력 ※ \n\n bucketlist_id : 이미지를 생성할 BucketList의 id (PK) 값을 입력 \n\n review_id : 이미지를 생성할 Review의 id (PK) 값을 입력 \n\n file : 원하는 이미지를 업로드"
    ),
)
async def create_image(
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

    if bucketlist_id is None and review_id is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="bucketlist_id와 review_id 둘 중 하나를 선택하세요.",
        )
    elif bucketlist_id is not None and review_id is not None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="bucketlist_id와 review_id를 모두 입력할 수 없습니다.",
        )
    else:
        with open(file_path, "wb") as fp:
            fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    await image_crud.create_image(
        db=db,
        data=file_url,
        bucketlist_id=bucketlist_id,
        review_id=review_id,
    )
    return {
        "data": file_url,
        "bucketlist_id": bucketlist_id,
        "review_id": review_id,
    }
