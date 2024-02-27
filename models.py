from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base


# 회원
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    password = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)  # 추후 변경


# 버킷 게시글
class BucketList(Base):
    __tablename__ = "bucketlist"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=True)
    bucket_image = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    category = Column(String, nullable=True)
    is_done = Column(Boolean, default=False, nullable=False)
    calender = Column(Date, nullable=True)
    # 외래키
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="bucketlist_users")


# 리뷰 게시글
class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    review_image = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    completed_at = Column(Date, nullable=True)
    # user 외래키
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="review_users")
    # bucketlist 외래키
    bucketlist_id = Column(Integer, ForeignKey("bucketlist.id"), nullable=False)
    bucketlist = relationship("BucketList", backref="reviews")
