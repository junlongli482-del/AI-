from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "us_users"  # 表名加前缀避免冲突

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), unique=True, nullable=True)  # 添加这行如果没有的话
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 新增：互动功能关系映射
    document_likes = relationship("DocumentLike", back_populates="user", cascade="all, delete-orphan")
    document_favorites = relationship("DocumentFavorite", back_populates="user", cascade="all, delete-orphan")
    document_comments = relationship("DocumentComment", back_populates="user", cascade="all, delete-orphan")

    # 🆕 新增：分享功能关系映射
    shares = relationship("DocumentShare", cascade="all, delete-orphan")