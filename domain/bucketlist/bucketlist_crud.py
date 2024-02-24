from datetime import datetime

from domain.bucketlist.bucketlist_schema import BucketListCreate

from models import BucketList
from sqlalchemy.orm import Session


def get_bucketlist_list(db: Session):
    bucketlist_list = db.query(BucketList).order_by(BucketList.create_at.desc()).all()
    return bucketlist_list


def get_bucketlist(db: Session, bucketlist_id: int):
    bucketlist = db.query(BucketList).get(bucketlist_id)
    return bucketlist


def create_bucketlist(db: Session, bucketlist_create: BucketListCreate):
    db_bucketlist = BucketList(
        title=bucketlist_create.title,
        content=bucketlist_create.content,
        image=bucketlist_create.image,
        category=bucketlist_create.category,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        calender=datetime.now(),
        is_done=False,
    )
    db.add(db_bucketlist)
    db.commit()
