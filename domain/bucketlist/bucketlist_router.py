from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.bucketlist import bucketlist_schema, bucketlist_crud
from domain.user.user_router import get_current_user
from models import User

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


# 버킷리스트 생성
@router.post("/create", status_code=status.HTTP_201_CREATED)
def bucketlist_create(
    _bucketlist_create: bucketlist_schema.BucketListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bucketlist_crud.create_bucketlist(
        db=db, bucketlist_create=_bucketlist_create, user=current_user
    )


# 버킷리스트 수정
@router.put("/update", status_code=status.HTTP_200_OK)
def bucketlist_update(
    _bucketlist_update: bucketlist_schema.BucketListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_bucketlist = bucketlist_crud.get_bucketlist(
        db, bucketlist_id=_bucketlist_update.bucketlist_id
    )
    if not db_bucketlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을수 없습니다."
        )
    if current_user.id != db_bucketlist.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="수정 권한이 없습니다."
        )
    bucketlist_crud.update_bucketlist(
        db=db, db_bucketlist=db_bucketlist, bucketlist_update=_bucketlist_update
    )


# 버킷리스트 삭제
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def bucketlist_delete(
    _bucketlist_delete: bucketlist_schema.BucketListDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_bucketlist = bucketlist_crud.get_bucketlist(
        db, bucketlist_id=_bucketlist_delete.bucketlist_id
    )
    if not db_bucketlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을수 없습니다."
        )
    if current_user.id != db_bucketlist.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="삭제 권한이 없습니다."
        )
    bucketlist_crud.delete_bucketlist(db=db, db_bucketlist=db_bucketlist)
