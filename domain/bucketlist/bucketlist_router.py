from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, get_async_db
from domain.bucketlist import bucketlist_schema, bucketlist_crud
from domain.user.user_router import get_current_user
from models import User

from starlette import status

router = APIRouter(
    prefix="/api/bucketlist",
)


# 모든 버킷리스트 가져오기
@router.get(
    "/list",
    response_model=bucketlist_schema.BucketListList,
    tags=(["BucketList"]),
    summary=("모든 버킷리스트 가져오기 (페이지네이션 적용)"),
    description=(
        "page : 몇 번째 페이지를 가져올 것인지 입력 \n\n size : 한 페이지당 몇 개의 글을 가져올 것인지 입력 \n\n keyword : 검색할 키워드 입력 (버킷리스트 제목/내용, 리뷰 제목/내용)"
    ),
)
async def bucketlist_list(
    db: Session = Depends(get_async_db),
    page: int = 0,
    size: int = 10,
    keyword: str = "",
):  # Depends를 사용하여 with문 대체
    total, _bucketlist_list = await bucketlist_crud.get_bucketlist_list(
        db, skip=page * size, limit=size, keyword=keyword
    )
    return {"total": total, "bucketlist_list": _bucketlist_list}


# 특정 버킷리스트 가져오기
@router.get(
    "/detail/{bucketlist_id}",
    response_model=bucketlist_schema.BucketList,
    tags=(["BucketList"]),
    summary=("특정 버킷리스트 가져오기"),
    description=("bucketlist_id : 가져오고싶은 BucketList의 id (PK) 값을 입력"),
)
async def bucketlist_detail(bucketlist_id: int, db: Session = Depends(get_async_db)):

    bucketlist = await bucketlist_crud.get_bucketlist(db, bucketlist_id=bucketlist_id)
    if not bucketlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글을 찾을 수 없습니다.",
        )
    return bucketlist


# 버킷리스트 생성
@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    tags=(["BucketList"]),
    summary=("버킷리스트 생성"),
    description=(
        "title : 제목 \n\n content : 내용 \n\n category : [음식점, 카페, 체험, 액티비티, 여행, 쇼핑, 운동, 게임, 영화, 기타] 중 선택 \n\n calender : 버킷리스트 예정일 ('0000-00-00' 형태로 입력)"
    ),
)
async def bucketlist_create(
    _bucketlist_create: bucketlist_schema.BucketListCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    await bucketlist_crud.create_bucketlist(
        db=db, bucketlist_create=_bucketlist_create, user=current_user
    )
    return {"status": "201", "success": "버킷리스트 생성완료"}


# 버킷리스트 수정
@router.put(
    "/update",
    status_code=status.HTTP_200_OK,
    tags=(["BucketList"]),
    summary=("버킷리스트 수정"),
    description=(
        "title : 제목 \n\n content : 내용 \n\n category : [음식점, 카페, 체험, 액티비티, 여행, 쇼핑, 운동, 게임, 영화, 기타] 중 선택 \n\n calender : '0000-00-00' 형태로 입력 \n\n bucketlist_id : 수정하고싶은 BucketList의 id (PK) 값을 입력"
    ),
)
async def bucketlist_update(
    _bucketlist_update: bucketlist_schema.BucketListUpdate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    db_bucketlist = await bucketlist_crud.get_bucketlist(
        db, bucketlist_id=_bucketlist_update.bucketlist_id
    )
    if not db_bucketlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 게시글을 찾을 수 없습니다.",
        )
    if current_user.id != db_bucketlist.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="수정 권한이 없습니다."
        )
    await bucketlist_crud.update_bucketlist(
        db=db, db_bucketlist=db_bucketlist, bucketlist_update=_bucketlist_update
    )
    return {"status": "200", "success": "버킷리스트 수정완료"}


# 버킷리스트 삭제
@router.delete(
    "/delete/{bucketlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=(["BucketList"]),
    summary=("버킷리스트 삭제"),
    description=("bucketlist_id : 삭제하고싶은 BucketList의 id (PK) 값을 입력"),
)
async def bucketlist_delete(
    bucketlist_id: int,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    db_bucketlist = await bucketlist_crud.get_bucketlist(
        db, bucketlist_id=bucketlist_id
    )
    if not db_bucketlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 게시글을 찾을 수 없습니다.",
        )
    if current_user.id != db_bucketlist.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="삭제 권한이 없습니다."
        )
    await bucketlist_crud.delete_bucketlist(db=db, db_bucketlist=db_bucketlist)
