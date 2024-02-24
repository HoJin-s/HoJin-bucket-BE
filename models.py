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
    create_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)  # 추후 변경


# 버킷 게시글
class BucketList(Base):
    __tablename__ = "bucketlist"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    create_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    is_done = Column(Boolean, default=False, nullable=False)
    calender = Column(Date, nullable=True)
    # 외래키
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="bucketlist_users")


# 버킷 내용
class BucketContent(Base):
    __tablename__ = "bucketcontent"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=True)
    create_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    # 외래키
    bucketlist_id = Column(Integer, ForeignKey("bucketlist.id"), nullable=False)
    bucketlist = relationship("BucketList", backref="bucketlist_contents")


class BucketImage(Base):
    __tablename__ = "bucketimage"

    id = Column(Integer, primary_key=True)
    image = Column(Text, nullable=True)
    # 외래키
    bucketcontent_id = Column(Integer, ForeignKey("bucketcontent.id"), nullable=False)
    bucketcontent = relationship("BucketContent", backref="bucketcontent_image")
