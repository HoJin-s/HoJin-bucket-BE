from datetime import datetime

from domain.bucketlist.bucketlist_schema import BucketListCreate

from models import BucketList, User
from sqlalchemy.orm import Session


# 버킷리스트 전체 가져오기
def get_bucketlist_list(db: Session, skip: int = 0, limit: int = 10):
    """
    skip은 조회한 데이터의 시작위치
    limit는 시작위치부터 가져올 데이터의 건수
    (300개의 데이터 중에서 21 ~ 30 번째 데이터를 가져오려면 skip은 20, limit는 10)
    """
    _bucketlist_list = db.query(BucketList).order_by(BucketList.created_at.desc())
    total = _bucketlist_list.count()
    bucketlist_list = _bucketlist_list.offset(skip).limit(limit).all()
    return total, bucketlist_list  # (전체 건수, 페이징 적용된 질문 목록)


# 특정 버킷리스트 가져오기
def get_bucketlist(db: Session, bucketlist_id: int):
    bucketlist = db.query(BucketList).get(bucketlist_id)
    return bucketlist


# 버킷리스트 생성하기
def create_bucketlist(db: Session, bucketlist_create: BucketListCreate, user: User):
    db_bucketlist = BucketList(
        title=bucketlist_create.title,
        content=bucketlist_create.content,
        image=bucketlist_create.image,
        category=bucketlist_create.category,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        calender=datetime.now(),
        is_done=False,
        user=user,
    )
    db.add(db_bucketlist)
    db.commit()
