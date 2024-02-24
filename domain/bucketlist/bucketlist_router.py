from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from domain.bucketlist import bucketlist_schema, bucketlist_crud
from starlette import status

router = APIRouter(
    prefix="/api/bucketlist",
)


# 모든 버킷리스트 가져오기
@router.get("/list", response_model=bucketlist_schema.BucketListList)
def bucketlist_list(
    db: Session = Depends(get_db), page: int = 0, size: int = 10
):  # Depends를 사용하여 with문 대체
    total, _bucketlist_list = bucketlist_crud.get_bucketlist_list(
        db, skip=page * size, limit=size
    )
    return {"total": total, "bucketlist_list": _bucketlist_list}


# 특정 버킷리스트 가져오기
@router.get("/detail/{bucketlist_id}", response_model=bucketlist_schema.BucketList)
def bucketlist_detail(bucketlist_id: int, db: Session = Depends(get_db)):
    bucketlist = bucketlist_crud.get_bucketlist(db, bucketlist_id=bucketlist_id)
    return bucketlist


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def bucketlist_create(
    _bucketlist_create: bucketlist_schema.BucketListCreate,
    db: Session = Depends(get_db),
):
    bucketlist_crud.create_bucketlist(db=db, bucketlist_create=_bucketlist_create)
