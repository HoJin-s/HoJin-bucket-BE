from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.bucketlist import bucketlist_crud
from domain.review import review_schema, review_crud
from domain.user.user_router import get_current_user
from models import User

from starlette import status

router = APIRouter(
    prefix="/api/review",
)


# 해당 리뷰 가져오기
@router.get("/detail/{review_id}", response_model=review_schema.Review)
def review_detail(review_id: int, db: Session = Depends(get_db)):
    review = review_crud.get_review(db, review_id=review_id)
    return review


# 리뷰 생성
@router.post("/create/{bucketlist_id}", status_code=status.HTTP_201_CREATED)
def review_create(
    bucketlist_id: int,
    _review_create: review_schema.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bucketlist = bucketlist_crud.get_bucketlist(db, bucketlist_id=bucketlist_id)
    if not bucketlist:
        raise HTTPException(status_code=404, detail="버킷리스트를 찾을 수 없습니다.")
    review_crud.create_review(
        db=db, bucketlist=bucketlist, review_create=_review_create, user=current_user
    )


# 리뷰 수정
@router.put("/update", status_code=status.HTTP_200_OK)
def review_update(
    _review_update: review_schema.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_review = review_crud.get_review(db, review_id=_review_update.review_id)
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을수 없습니다."
        )
    if current_user.id != db_review.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="수정 권한이 없습니다."
        )
    review_crud.update_review(db=db, db_review=db_review, review_update=_review_update)


# 리뷰 삭제
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def review_delete(
    _review_delete: review_schema.ReviewDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_review = review_crud.get_review(db, review_id=_review_delete.review_id)
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을수 없습니다."
        )
    if current_user.id != db_review.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="삭제 권한이 없습니다."
        )
    review_crud.delete_review(db=db, db_review=db_review)
