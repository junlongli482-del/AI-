"""
文件上传模块 - 数据模型
功能：定义文件上传相关的数据结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class UploadRecord(Base):
    """
    文件上传记录表
    记录所有文件上传的详细信息和状态
    """
    __tablename__ = "us_upload_records"

    id = Column(Integer, primary_key=True, index=True)

    # 文件基本信息
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    stored_filename = Column(String(255), nullable=False, comment="存储文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(Integer, nullable=False, comment="文件大小(字节)")

    # 🔧 直接使用字符串枚举，避免Python枚举类转换问题
    file_type = Column(Enum('md', 'pdf'), nullable=False, comment="文件类型")
    status = Column(Enum('uploading', 'uploaded', 'validated', 'failed', 'deleted'),
                   default='uploading', comment="文件状态")

    mime_type = Column(String(100), nullable=False, comment="MIME类型")
    validation_message = Column(Text, comment="验证结果信息")

    # 关联信息
    user_id = Column(Integer, nullable=False, comment="上传用户ID")
    document_id = Column(Integer, nullable=True, comment="关联文档ID")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<UploadRecord(id={self.id}, filename={self.original_filename}, status={self.status})>"