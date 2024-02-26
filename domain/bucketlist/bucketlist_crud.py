from datetime import datetime

from domain.bucketlist.bucketlist_schema import BucketListCreate, BucketListUpdate

from sqlalchemy import and_
from models import BucketList, User, Review
from sqlalchemy.orm import Session


# 버킷리스트 전체 가져오기
def get_bucketlist_list(db: Session, skip: int = 0, limit: int = 10, keyword: str = ""):
    """
    - skip은 조회한 데이터의 시작위치
    - limit는 시작위치부터 가져올 데이터의 건수
    (300개의 데이터 중에서 21 ~ 30 번째 데이터를 가져오려면 skip은 20, limit는 10)

    - 검색어(keyword)에 값이 있으면 그 값을 OR 조건으로 검색
    """
    bucketlist_list = db.query(BucketList)
    if keyword:
        search = f"%%{keyword}%%"
        """
        Review / User 모델을 outerjoin한 서브쿼리
        Review.bucketlist_id : 서브쿼리와 BucketList 모델을 연결할수 있는 질문 id
        Review.content, User.username : 리뷰내용, 리뷰 작성자
        """
        sub_query = (
            db.query(Review.bucketlist_id, Review.content, User.username)
            .outerjoin(User, and_(Review.user_id == User.id))
            .subquery()
        )
        """
        서브쿼리 / BuckList 모델을 outerjoin
        .c 는 서브쿼리의 조회 항목을 의미함.
        ex) sub_query.c.bucketlist_id : 서브쿼리의 조회 항목 중 bucketlist_id 의미
        """
        bucketlist_list = (
            bucketlist_list.outerjoin(User)
            .outerjoin(sub_query, and_(sub_query.c.bucketlist_id == BucketList.id))
            .filter(
                BucketList.title.ilike(search)  # 버킷리스트 제목
                | BucketList.content.ilike(search)  # 버킷리스트 내용
                | User.username.ilike(search)  # 버킷리스트 작성자
                | sub_query.c.content.ilike(search)  # 리뷰 내용
                | sub_query.c.username.ilike(search)  # 리뷰 작성자
            )
        )
    # distinct 함수를 사용하여 중복 데이터 제거
    total = bucketlist_list.distinct().count()
    bucketlist_list = (
        bucketlist_list.order_by(BucketList.created_at.desc())
        .offset(skip)
        .limit(limit)
        .distinct()
        .all()
    )

    return total, bucketlist_list  # 전체 건수, 페이징 적용된 질문 목록


# 특정 버킷리스트 가져오기
def get_bucketlist(db: Session, bucketlist_id: int):
    bucketlist = db.query(BucketList).get(bucketlist_id)
    return bucketlist


# 버킷리스트 생성하기
def create_bucketlist(db: Session, bucketlist_create: BucketListCreate, user: User):
    db_bucketlist = BucketList(
        title=bucketlist_create.title,
        content=bucketlist_create.content,
        bucket_image=bucketlist_create.bucket_image,
        created_at=datetime.now(),
        category=bucketlist_create.category,
        calender=bucketlist_create.calender,
        user=user,
    )
    db.add(db_bucketlist)
    db.commit()


# 버킷리스트 수정하기
def update_bucketlist(
    db: Session, db_bucketlist: BucketList, bucketlist_update: BucketListUpdate
):
    db_bucketlist.title = bucketlist_update.title
    db_bucketlist.content = bucketlist_update.content
    db_bucketlist.bucket_image = bucketlist_update.bucket_image
    db_bucketlist.category = bucketlist_update.category
    db_bucketlist.updated_at = datetime.now()
    db_bucketlist.calender = bucketlist_update.calender
    db.add(db_bucketlist)
    db.commit()


# 버킷리스트 삭제하기
def delete_bucketlist(db: Session, db_bucketlist: BucketList):
    db.delete(db_bucketlist)
    db.commit()
