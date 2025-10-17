from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class EditorSession(Base):
    """编辑器会话模型"""
    __tablename__ = "us_editor_sessions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("us_users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    is_draft = Column(Boolean, default=True)
    session_type = Column(Enum('new_document', 'edit_document'), default='new_document')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 单向关系 - 不需要修改现有模型
    ai_optimizations = relationship("AIOptimization", cascade="all, delete-orphan")


class AIOptimization(Base):
    """AI优化记录模型"""
    __tablename__ = "us_ai_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("us_editor_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id"), nullable=False)
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text, nullable=False)
    optimization_prompt = Column(Text, nullable=True)
    ai_provider = Column(String(50), default='default')
    status = Column(Enum('pending', 'completed', 'failed'), default='completed')
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 单向关系
    session = relationship("EditorSession")