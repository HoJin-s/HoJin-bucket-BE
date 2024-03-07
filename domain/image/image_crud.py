from sqlalchemy.orm import Session, selectinload
from models import Image
from sqlalchemy import select


# 특정 이미지 가져오기
async def get_image(db: Session, image_id: int):
    review = await db.execute(select(Image).filter(Image.id == image_id))
    return review.scalar_one_or_none()


# 이미지 생성하기
async def create_image(db: Session, data, bucketlist_id, review_id):
    db_image = Image(
        data=data,
        bucketlist_id=bucketlist_id,
        review_id=review_id,
    )
    db.add(db_image)
    await db.commit()


# 이미지 삭제하기
async def delete_image(db: Session, db_image: Image):
    await db.delete(db_image)
    await db.commit()
