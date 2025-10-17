from sqlalchemy import Column, Integer, String, Text, Enum, DECIMAL, Boolean, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class AIReviewLog(Base):
    __tablename__ = "us_ai_review_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)
    review_type = Column(Enum('content_quality', 'content_safety', 'format_check', 'length_check'), nullable=False)
    ai_provider = Column(String(50), default='default')
    file_id = Column(String(100), nullable=True)  # AI服务返回的文件ID
    review_prompt = Column(Text, nullable=False)  # 使用的审核提示词
    ai_response = Column(Text, nullable=True)     # AI的完整回复
    review_result = Column(Enum('pending', 'passed', 'failed', 'error'), default='pending')
    failure_reason = Column(Text, nullable=True)  # 审核失败的具体原因
    confidence_score = Column(DECIMAL(3,2), nullable=True)  # AI的置信度分数
    review_duration = Column(Integer, nullable=True)  # 审核耗时（秒）
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 关系映射（单向关系，避免修改现有模型）
    # document = relationship("Document")  # 如果需要可以添加
    # user = relationship("User")          # 如果需要可以添加

class ReviewRule(Base):
    __tablename__ = "us_review_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False, unique=True)
    rule_type = Column(Enum('length_limit', 'format_check', 'content_policy', 'quality_standard'), nullable=False)
    rule_config = Column(JSON, nullable=False)  # 规则配置（JSON格式）
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 规则优先级
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())