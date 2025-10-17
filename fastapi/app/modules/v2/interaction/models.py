from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DocumentLike(Base):
    """文档点赞表"""
    __tablename__ = "us_document_likes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    document = relationship("Document", back_populates="likes")
    user = relationship("User")

    __table_args__ = (
        Index('unique_user_document_like', 'user_id', 'document_id', unique=True),
        Index('idx_document_id', 'document_id'),
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
    )


class DocumentFavorite(Base):
    """文档收藏表"""
    __tablename__ = "us_document_favorites"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    document = relationship("Document", back_populates="favorites")
    user = relationship("User")

    __table_args__ = (
        Index('unique_user_document_favorite', 'user_id', 'document_id', unique=True),
        Index('idx_document_id', 'document_id'),
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
    )


class DocumentComment(Base):
    """文档评论表"""
    __tablename__ = "us_document_comments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("us_document_comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    document = relationship("Document", back_populates="comments")
    user = relationship("User")
    parent = relationship("DocumentComment", remote_side=[id], back_populates="replies")
    replies = relationship("DocumentComment", back_populates="parent", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_user_id', 'user_id'),
        Index('idx_parent_id', 'parent_id'),
        Index('idx_created_at', 'created_at'),
    )


class DocumentInteractionStats(Base):
    """文档互动统计表"""
    __tablename__ = "us_document_interaction_stats"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    like_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    document = relationship("Document", back_populates="interaction_stats")

    __table_args__ = (
        Index('idx_document_id', 'document_id'),
    )