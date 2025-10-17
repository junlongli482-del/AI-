from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from datetime import datetime

# 导入现有的基类
from ..document_manager.models import Base


# 🔧 删除Python枚举类定义，直接使用字符串枚举
# class ShareType(enum.Enum):
#     PUBLIC = "public"
#     PRIVATE = "private"
#     PASSWORD = "password"

# class ShareStatus(enum.Enum):
#     ACTIVE = "active"
#     EXPIRED = "expired"
#     DISABLED = "disabled"

class DocumentShare(Base):
    __tablename__ = "us_document_shares"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("us_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("us_users.id", ondelete="CASCADE"), nullable=False)

    # 分享配置
    share_code = Column(String(32), unique=True, nullable=False, index=True)

    # 🔧 修复：直接使用字符串枚举
    share_type = Column(
        Enum('public', 'private', 'password', name='share_type_enum'),
        default='public',
        nullable=False
    )

    share_password = Column(String(100), nullable=True)

    # 权限设置
    allow_download = Column(Boolean, default=True)
    allow_comment = Column(Boolean, default=True)

    # 状态管理
    # 🔧 修复：直接使用字符串枚举
    status = Column(
        Enum('active', 'expired', 'disabled', name='share_status_enum'),
        default='active',
        nullable=False
    )

    expire_time = Column(DateTime, nullable=True)

    # 统计信息
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ShareAccessLog(Base):
    __tablename__ = "us_share_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(Integer, ForeignKey("us_document_shares.id", ondelete="CASCADE"), nullable=False)

    # 访问信息
    visitor_ip = Column(String(45), nullable=True)
    visitor_user_agent = Column(Text, nullable=True)
    visitor_user_id = Column(Integer, ForeignKey("us_users.id", ondelete="SET NULL"), nullable=True)

    # 访问行为
    access_type = Column(String(20), nullable=False)  # VIEW, DOWNLOAD, COMMENT
    access_result = Column(String(50), default="success")

    # 时间戳
    accessed_at = Column(DateTime, default=datetime.utcnow)