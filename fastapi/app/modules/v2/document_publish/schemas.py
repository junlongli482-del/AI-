from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# 发布请求模型
class PublishRequest(BaseModel):
    document_id: int = Field(..., description="文档ID")
    publish_reason: Optional[str] = Field(None, max_length=500, description="发布说明")
    publish_config: Optional[Dict[str, Any]] = Field(None, description="发布配置")


# 撤回发布请求
class UnpublishRequest(BaseModel):
    unpublish_reason: str = Field(..., max_length=500, description="撤回原因")


# 发布记录响应模型
class PublishRecordResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    publish_version: int
    publish_status: str
    publish_time: Optional[datetime]
    unpublish_time: Optional[datetime]
    publish_reason: Optional[str]
    unpublish_reason: Optional[str]
    review_id: Optional[int]
    view_count: int
    is_featured: bool
    publish_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 发布历史响应模型
class PublishHistoryResponse(BaseModel):
    id: int
    publish_record_id: int
    document_id: int
    action_type: str
    action_reason: Optional[str]
    old_status: Optional[str]
    new_status: Optional[str]
    operator_id: Optional[int]
    action_time: datetime

    class Config:
        from_attributes = True


# 分页查询模型
class PublishedDocumentsQuery(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    status: Optional[str] = Field(None, description="发布状态筛选")
    is_featured: Optional[bool] = Field(None, description="是否精选")


# 发布统计响应
class PublishStatsResponse(BaseModel):
    total_published: int
    total_drafts: int
    pending_review: int
    today_published: int
    featured_count: int
    total_views: int


# 文档发布详情响应
class DocumentPublishDetail(BaseModel):
    # 文档基本信息
    document_id: int
    title: str
    summary: Optional[str]
    file_type: str
    created_at: datetime

    # 发布信息
    publish_record: Optional[PublishRecordResponse]

    # 发布历史
    publish_history: List[PublishHistoryResponse]

    class Config:
        from_attributes = True


# 已发布文档列表项
class PublishedDocumentItem(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    file_type: str
    user_id: int
    publish_time: datetime
    view_count: int
    is_featured: bool

    class Config:
        from_attributes = True


# 分页响应模型
class PublishedDocumentsResponse(BaseModel):
    items: List[PublishedDocumentItem]
    total: int
    page: int
    size: int
    pages: int