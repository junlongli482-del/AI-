from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 🔧 保持Pydantic枚举不变（用于API验证）
class ShareType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PASSWORD = "password"

class ShareStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"

class AccessType(str, Enum):
    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"
    COMMENT = "COMMENT"

# 其余代码保持不变...


# 创建分享请求
class CreateShareRequest(BaseModel):
    document_id: int = Field(..., description="文档ID")
    share_type: ShareType = Field(ShareType.PUBLIC, description="分享类型")
    share_password: Optional[str] = Field(None, description="分享密码（密码保护时必填）")
    allow_download: bool = Field(True, description="允许下载")
    allow_comment: bool = Field(True, description="允许评论")
    expire_hours: Optional[int] = Field(None, description="过期时间（小时），NULL表示永不过期")

    @validator('share_password')
    def validate_password(cls, v, values):
        if values.get('share_type') == ShareType.PASSWORD and not v:
            raise ValueError('密码保护分享必须设置密码')
        if values.get('share_type') != ShareType.PASSWORD and v:
            raise ValueError('非密码保护分享不能设置密码')
        return v


# 更新分享请求
class UpdateShareRequest(BaseModel):
    share_type: Optional[ShareType] = Field(None, description="分享类型")
    share_password: Optional[str] = Field(None, description="分享密码")
    allow_download: Optional[bool] = Field(None, description="允许下载")
    allow_comment: Optional[bool] = Field(None, description="允许评论")
    expire_hours: Optional[int] = Field(None, description="过期时间（小时）")
    status: Optional[ShareStatus] = Field(None, description="分享状态")


# 访问分享请求
class AccessShareRequest(BaseModel):
    password: Optional[str] = Field(None, description="分享密码（密码保护时必填）")


# 分享响应
class ShareResponse(BaseModel):
    id: int
    document_id: int
    share_code: str
    share_type: ShareType
    share_url: str
    allow_download: bool
    allow_comment: bool
    status: ShareStatus
    expire_time: Optional[datetime]
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime

    # 文档信息
    document_title: str
    document_summary: Optional[str]

    class Config:
        from_attributes = True


# 分享详情响应
class ShareDetailResponse(ShareResponse):
    # 访问统计
    today_views: int
    week_views: int
    month_views: int

    # 最近访问记录
    recent_access_logs: List['AccessLogResponse']


# 访问记录响应
class AccessLogResponse(BaseModel):
    id: int
    access_type: AccessType
    access_result: str
    visitor_ip: Optional[str]
    visitor_user_id: Optional[int]
    visitor_username: Optional[str]
    accessed_at: datetime

    class Config:
        from_attributes = True


# 分享统计响应
class ShareStatsResponse(BaseModel):
    total_shares: int
    active_shares: int
    expired_shares: int
    disabled_shares: int
    total_views: int
    total_downloads: int
    today_views: int
    week_views: int
    month_views: int
    popular_shares: List[ShareResponse]


# 分页响应
class ShareListResponse(BaseModel):
    items: List[ShareResponse]
    total: int
    page: int
    size: int
    pages: int


# 公开访问文档响应
class PublicDocumentResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    summary: Optional[str]
    file_type: str
    file_size: int
    author_username: str
    publish_time: Optional[datetime]
    view_count: int

    # 分享配置
    allow_download: bool
    allow_comment: bool

    class Config:
        from_attributes = True