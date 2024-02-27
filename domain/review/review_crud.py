from datetime import datetime

from domain.review.review_schema import ReviewCreate, ReviewUpdate

from models import Review, BucketList, User
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select


# 특정 리뷰 가져오기
async def get_review(db: Session, review_id: int):
    review = await db.execute(
        select(Review).filter(Review.id == review_id).options(selectinload(Review.user))
    )
    return review.scalar_one()


# 리뷰 생성하기
async def create_review(
    db: Session, review_create: ReviewCreate, user: User, bucketlist: BucketList
):
    db_review = Review(
        title=review_create.title,
        content=review_create.content,
        review_image=review_create.review_image,
        created_at=datetime.now(),
        completed_at=review_create.completed_at,
        user=user,
        bucketlist=bucketlist,
    )
    db.add(db_review)
    await db.commit()


# 리뷰 수정하기
async def update_review(db: Session, db_review: Review, review_update: ReviewUpdate):
    db_review.title = review_update.title
    db_review.content = review_update.content
    db_review.review_image = review_update.review_image
    db_review.updated_at = datetime.now()
    db_review.completed_at = review_update.completed_at
    db.add(db_review)
    await db.commit()


# 리뷰 삭제하기
async def delete_review(db: Session, db_review: Review):
    await db.delete(db_review)
    await db.commit()
