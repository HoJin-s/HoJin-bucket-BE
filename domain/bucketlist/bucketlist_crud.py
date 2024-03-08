from datetime import datetime
from fastapi import HTTPException
from domain.bucketlist.bucketlist_schema import BucketListCreate, BucketListUpdate
from starlette import status
from sqlalchemy import and_, select, func
from models import BucketList, User, Review
from sqlalchemy.orm import Session, selectinload


# 버킷리스트 전체 가져오기
async def get_bucketlist_list(
    db: Session, skip: int = 0, limit: int = 10, keyword: str = ""
):
    """
    - skip은 조회한 데이터의 시작위치
    - limit는 시작위치부터 가져올 데이터의 건수
      (300개의 데이터 중에서 21 ~ 30 번째 데이터를 가져오려면 skip은 20, limit는 10)

    - 검색어(keyword)에 값이 있으면 그 값을 OR 조건으로 검색
    - 비동기로 데이터를 조회하기 위해서는 db.query(Query) 대신 db.execute(select(Query))와 같은 방식을 사용해야함
    """
    query = select(BucketList)
    if keyword:
        search = f"%%{keyword}%%"
        """
        Review / User 모델을 outerjoin한 서브쿼리
        Review.bucketlist_id : 서브쿼리와 BucketList 모델을 연결할수 있는 질문 id
        Review.content, User.username : 리뷰내용, 리뷰 작성자
        """
        sub_query = (
            select(Review.bucketlist_id, Review.title, Review.content, User.username)
            .outerjoin(User, and_(Review.user_id == User.id))
            .subquery()
        )
        """
        서브쿼리 / BuckList 모델을 outerjoin
        .c 는 서브쿼리의 조회 항목을 의미함.
        ex) sub_query.c.bucketlist_id : 서브쿼리의 조회 항목 중 bucketlist_id 의미
        """
        query = (
            query.outerjoin(User)
            .outerjoin(sub_query, and_(sub_query.c.bucketlist_id == BucketList.id))
            .filter(
                BucketList.title.ilike(search)  # 버킷리스트 제목
                | BucketList.content.ilike(search)  # 버킷리스트 내용
                | User.username.ilike(search)  # 버킷리스트 작성자
                | sub_query.c.title.ilike(search)  # 리뷰 제목
                | sub_query.c.content.ilike(search)  # 리뷰 내용
                | sub_query.c.username.ilike(search)  # 리뷰 작성자
            )
        )
    total = await db.execute(select(func.count()).select_from(query.subquery()))
    bucketlist_list = await db.execute(
        query.order_by(BucketList.created_at.desc())
        .offset(skip)
        .limit(limit)
        .distinct()
        .options(selectinload(BucketList.reviews).selectinload(Review.user))
        .options(selectinload(BucketList.user))
    )

    return (
        total.scalar_one(),
        bucketlist_list.scalars().fetchall(),
    )  # 전체 건수, 페이징 적용된 질문 목록


# 특정 버킷리스트 가져오기
async def get_bucketlist(db: Session, bucketlist_id: int):
    bucketlist = await db.execute(
        select(BucketList)
        .filter(BucketList.id == bucketlist_id)
        .options(selectinload(BucketList.reviews).selectinload(Review.user))
        .options(selectinload(BucketList.user))
    )
    return bucketlist.scalar_one_or_none()


# 버킷리스트 생성하기
async def create_bucketlist(
    db: Session, bucketlist_create: BucketListCreate, user: User
):
    existing_bucketlist_title = await db.execute(
        select(BucketList).filter_by(title=bucketlist_create.title)
    )
    if existing_bucketlist_title:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="입력한 제목이 이미 존재합니다.",
        )

    db_bucketlist = BucketList(
        title=bucketlist_create.title,
        content=bucketlist_create.content,
        created_at=datetime.now(),
        category=bucketlist_create.category,
        calender=bucketlist_create.calender,
        user=user,
    )
    db.add(db_bucketlist)
    await db.commit()


# 버킷리스트 수정하기
async def update_bucketlist(
    db: Session, db_bucketlist: BucketList, bucketlist_update: BucketListUpdate
):
    db_bucketlist.title = bucketlist_update.title
    db_bucketlist.content = bucketlist_update.content
    db_bucketlist.category = bucketlist_update.category
    db_bucketlist.updated_at = datetime.now()
    db_bucketlist.calender = bucketlist_update.calender
    db.add(db_bucketlist)
    await db.commit()


# 버킷리스트 삭제하기
async def delete_bucketlist(db: Session, db_bucketlist: BucketList):
    await db.delete(db_bucketlist)
    await db.commit()
