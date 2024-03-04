from sqlalchemy.orm import Session
from models import Image


# 이미지 생성하기
async def create_image(db: Session, data, bucketlist_id, review_id):
    db_image = Image(
        data=data,
        bucketlist_id=bucketlist_id,
        review_id=review_id,
    )
    db.add(db_image)
    await db.commit()
