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
from enum import Enum
from sqlalchemy import Enum as SQLEnum


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


# Enum 정의
class BucketListCategoryEnum(str, Enum):
    음식점 = "음식점"
    카페 = "카페"
    체험 = "체험"
    액티비티 = "액티비티"
    여행 = "여행"
    쇼핑 = "쇼핑"
    운동 = "운동"
    게임 = "게임"
    영화 = "영화"
    기타 = "기타"


# 버킷 게시글
class BucketList(Base):
    __tablename__ = "bucketlist"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    category = Column(SQLEnum(BucketListCategoryEnum), nullable=True)
    is_done = Column(Boolean, default=False, nullable=False)
    calender = Column(Date, nullable=True)
    # 외래키
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="bucketlist_users")
    # Cascade 설정
    reviews = relationship(
        "Review",
        backref="bucketlist",
        cascade="all, delete-orphan",
    )
    images = relationship(
        "Image",
        backref="bucketlist",
        cascade="all, delete-orphan",
    )


# 리뷰 게시글
class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    completed_at = Column(Date, nullable=True)
    # user 외래키
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="review_users")
    # bucketlist 외래키
    bucketlist_id = Column(Integer, ForeignKey("bucketlist.id"), nullable=False)
    # Cascade 설정
    images = relationship(
        "Image",
        backref="review",
        cascade="all, delete-orphan",
    )


# 버킷리스트 / 리뷰 이미지
class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    data = Column(String, nullable=False)

    # bucketlist 외래키
    bucketlist_id = Column(Integer, ForeignKey("bucketlist.id"), nullable=True)

    # review 외래키
    review_id = Column(Integer, ForeignKey("review.id"), nullable=True)
