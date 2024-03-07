from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import event
from database import get_async_db
from domain.image import image_crud
from models import BucketList, Image, Review, User
from domain.user.user_router import get_current_user
from starlette import status
from domain.image import image_schema
import os
import uuid
from dotenv import load_dotenv

load_dotenv(override=True)
BE_URL = os.getenv("BE_URL")

router = APIRouter(
    prefix="/api/image",
)

UPLOAD_DIR = "./image_file"


# 특정 이미지 가져오기
@router.get(
    "/detail/{image_id}",
    response_model=image_schema.Image,
    tags=(["Image"]),
    summary=("특정 이미지 가져오기"),
    description=("image_id : 가져오고싶은 Image의 id (PK) 값을 입력"),
)
async def image_detail(
    image_id: int,
    db: Session = Depends(get_async_db),
):
    image = await image_crud.get_image(db, image_id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 이미지를 찾을 수 없습니다.",
        )
    return image


# 이미지 생성하기
@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=image_schema.ImageCreate,
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
    current_user: User = Depends(get_current_user),
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    content = await file.read()
    filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경
    file_path = os.path.join(UPLOAD_DIR, filename)
    file_url = f"{BE_URL}/image_file\\{filename}"

    if bucketlist_id is not None:
        # bucketlist_id가 유효한지 확인
        bucketlist = await db.get(BucketList, bucketlist_id)
        if not bucketlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 버킷리스트를 찾을 수 없습니다.",
            )
        if current_user.id != bucketlist.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="생성 권한이 없습니다."
            )

    if review_id is not None:
        # review_id가 유효한지 확인
        review = await db.get(Review, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 리뷰를 찾을 수 없습니다.",
            )
        if current_user.id != review.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="생성 권한이 없습니다."
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


# 이미지 삭제하기
@router.delete(
    "/delete/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=(["Image"]),
    summary=("이미지 삭제"),
    description=("image_id : 이미지를 삭제할 Image의 id (PK) 값을 입력"),
)
async def delete_image(
    image_id=int,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    db_image = await db.get(Image, image_id)
    if not db_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 이미지를 찾을 수 없습니다.",
        )
    else:
        bucketlist = await db.get(BucketList, db_image.bucketlist_id)
        review = await db.get(Review, db_image.review_id)
        if bucketlist is not None:
            if current_user.id != bucketlist.user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="삭제 권한이 없습니다.",
                )
        if review is not None:
            if current_user.id != review.user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="삭제 권한이 없습니다.",
                )

    await image_crud.delete_image(db=db, db_image=db_image)


# 이미지가 DB에서 삭제될 때, 해당 이미지 파일을 sqlalchemy의 event.listen으로 삭제하는 함수
# 이벤트 리스너는 동기적인 방식으로 동작하므로, 하나의 트랜젝션이라고 생각하여 동기방식으로 구현
def delete_image_file(target):
    target_data = target.data.split("/")[3][11:]
    file_path = os.path.join(UPLOAD_DIR, target_data)
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_image_file_on_delete(mapper, connection, target):
    delete_image_file(target)


event.listen(Image, "before_delete", delete_image_file_on_delete)
