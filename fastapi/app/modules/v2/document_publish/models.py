from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class PublishRecord(Base):
    __tablename__ = "us_publish_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)
    publish_version = Column(Integer, default=1)
    publish_status = Column(String(20), default="draft")  # 使用字符串枚举
    publish_time = Column(DateTime, nullable=True)
    unpublish_time = Column(DateTime, nullable=True)
    publish_reason = Column(Text, nullable=True)
    unpublish_reason = Column(Text, nullable=True)
    review_id = Column(Integer, nullable=True)
    view_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    publish_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PublishHistory(Base):
    __tablename__ = "us_publish_history"

    id = Column(Integer, primary_key=True, index=True)
    publish_record_id = Column(Integer, ForeignKey("us_publish_records.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(20), nullable=False)  # submit, approve, reject, publish, unpublish, edit
    action_reason = Column(Text, nullable=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)
    operator_id = Column(Integer, ForeignKey("us_users.id", ondelete="SET NULL"), nullable=True)
    action_time = Column(DateTime, default=datetime.utcnow)