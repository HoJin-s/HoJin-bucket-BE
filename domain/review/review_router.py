from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, get_async_db
from domain.bucketlist import bucketlist_crud
from domain.review import review_schema, review_crud
from domain.user.user_router import get_current_user
from models import User

from starlette import status

router = APIRouter(
    prefix="/api/review",
)


# 특정 리뷰 가져오기
@router.get(
    "/detail/{review_id}",
    response_model=review_schema.Review,
    tags=(["Review"]),
    summary=("특정 리뷰 가져오기"),
    description=("review_id : 가져오고싶은 Review의 id (PK) 값을 입력"),
)
async def review_detail(review_id: int, db: Session = Depends(get_async_db)):
    review = await review_crud.get_review(db, review_id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 리뷰를 찾을 수 없습니다.",
        )
    return review


# 리뷰 생성
@router.post(
    "/create/{bucketlist_id}",
    status_code=status.HTTP_201_CREATED,
    tags=(["Review"]),
    summary=("리뷰 생성"),
    description=(
        "title : 제목 \n\n content : 내용 \n\n completed_at : 버킷리스트 완료 날짜 ('0000-00-00' 형태로 입력)"
    ),
)
async def review_create(
    bucketlist_id: int,
    _review_create: review_schema.ReviewCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    bucketlist = await bucketlist_crud.get_bucketlist(db, bucketlist_id=bucketlist_id)
    if not bucketlist:
        raise HTTPException(status_code=404, detail="버킷리스트를 찾을 수 없습니다.")
    await review_crud.create_review(
        db=db, bucketlist=bucketlist, review_create=_review_create, user=current_user
    )


# 리뷰 수정
@router.put(
    "/update",
    status_code=status.HTTP_200_OK,
    tags=(["Review"]),
    summary=("리뷰 수정"),
    description=(
        "title : 제목 \n\n content : 내용 \n\n completed_at : 버킷리스트 완료 날짜 ('0000-00-00' 형태로 입력) \n\n review_id : 수정하고싶은 Review의 id (PK) 값을 입력"
    ),
)
async def review_update(
    _review_update: review_schema.ReviewUpdate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    db_review = await review_crud.get_review(db, review_id=_review_update.review_id)
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 리뷰를 찾을 수 없습니다.",
        )
    if current_user.id != db_review.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="수정 권한이 없습니다."
        )
    await review_crud.update_review(
        db=db, db_review=db_review, review_update=_review_update
    )


# 리뷰 삭제
@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=(["Review"]),
    summary=("리뷰 삭제"),
    description=("review_id : 삭제하고싶은 Review의 id (PK) 값을 입력"),
)
async def review_delete(
    _review_delete: review_schema.ReviewDelete,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    db_review = await review_crud.get_review(db, review_id=_review_delete.review_id)
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 리뷰를 찾을 수 없습니다.",
        )
    if current_user.id != db_review.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="삭제 권한이 없습니다."
        )
    await review_crud.delete_review(db=db, db_review=db_review)
