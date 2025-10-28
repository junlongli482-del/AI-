"""
文档管理模块 - 数据模型
功能：定义文件夹和文档的ORM模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.modules.v1.user_register.models import User
import enum

class FolderLevel(enum.Enum):
    """文件夹层级枚举"""
    ROOT = 1      # 根目录
    LEVEL_1 = 2   # 一级文件夹
    LEVEL_2 = 3   # 二级文件夹

class DocumentStatus(enum.Enum):
    """文档状态枚举（用于API响应）"""
    DRAFT = "draft"
    PUBLISHED = "published"
    REVIEW_FAILED = "review_failed"

class FileType(enum.Enum):
    """文件类型枚举（用于API响应）"""
    MD = "md"
    PDF = "pdf"

class Folder(Base):
    """文件夹模型"""
    __tablename__ = "us_folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="文件夹名称")
    parent_id = Column(Integer, ForeignKey("us_folders.id", ondelete="CASCADE"),
                      nullable=True, comment="父文件夹ID")
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"),
                    nullable=False, comment="所属用户ID")
    level = Column(Integer, default=1, comment="层级：1-根目录，2-一级，3-二级")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 关系定义
    children = relationship("Folder", backref="parent", remote_side=[id])
    documents = relationship("Document", back_populates="folder")
    user = relationship("User", foreign_keys=[user_id])

class Document(Base):
    """文档模型"""
    __tablename__ = "us_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="文档标题")
    content = Column(Text, nullable=True, comment="文档内容（MD格式）")
    file_path = Column(String(500), nullable=True, comment="上传文件路径")

    # 🔧 关键修改：直接使用字符串枚举，避免Python枚举类转换问题
    file_type = Column(
        Enum('md', 'pdf', name='file_type_enum'),
        nullable=False,
        default='md',
        comment="文件类型"
    )

    file_size = Column(Integer, default=0, comment="文件大小（字节）")
    summary = Column(Text, nullable=True, comment="用户填写的简短摘要")

    # 🔧 关键修改：直接使用字符串枚举，避免Python枚举类转换问题
    status = Column(
        Enum('draft', 'published', 'review_failed', name='document_status_enum'),
        default='draft',
        comment="文档状态"
    )

    publish_time = Column(TIMESTAMP, nullable=True, comment="发布时间")
    review_message = Column(Text, nullable=True, comment="AI审核失败原因")
    folder_id = Column(Integer, ForeignKey("us_folders.id", ondelete="SET NULL"),
                      nullable=True, comment="所属文件夹ID")
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"),
                    nullable=False, comment="作者ID")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 🆕 文档更新功能字段
    pending_title = Column(String(200), nullable=True, comment='待审核标题')
    pending_content = Column(Text, nullable=True, comment='待审核内容')
    pending_summary = Column(Text, nullable=True, comment='待审核摘要')
    has_pending_update = Column(Boolean, default=False, comment='是否有待审核更新')

    # 关系定义
    folder = relationship("Folder", back_populates="documents")
    user = relationship("User", foreign_keys=[user_id])

    # 添加以下关系映射（在类的最后）（interaction新增）
    likes = relationship("DocumentLike", back_populates="document", cascade="all, delete-orphan")
    favorites = relationship("DocumentFavorite", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("DocumentComment", back_populates="document", cascade="all, delete-orphan")
    interaction_stats = relationship("DocumentInteractionStats", back_populates="document", uselist=False, cascade="all, delete-orphan")

    # 🆕 新增：分享功能关系映射
    shares = relationship("DocumentShare", cascade="all, delete-orphan")

    # 在现有字段后添加
    has_published_version = Column(Boolean, default=False, comment='是否曾经发布过')