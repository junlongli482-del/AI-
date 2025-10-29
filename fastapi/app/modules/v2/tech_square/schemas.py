# app/modules/v2/tech_square/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class SortOption(str, Enum):
    """排序选项枚举"""
    LATEST = "latest"
    POPULAR = "popular"
    RECOMMENDED = "recommended"


class TimeFilter(str, Enum):
    """时间筛选枚举"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"


class FileTypeFilter(str, Enum):
    """文件类型筛选枚举"""
    MD = "md"
    PDF = "pdf"


# 请求模型
class DocumentListRequest(BaseModel):
    """文档列表请求参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    file_type: Optional[FileTypeFilter] = Field(None, description="文件类型筛选")
    time_filter: Optional[TimeFilter] = Field(None, description="时间筛选")
    sort_by: SortOption = Field(SortOption.LATEST, description="排序方式")


class SearchRequest(BaseModel):
    """搜索请求参数"""
    keyword: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=50, description="每页数量")
    file_type: Optional[FileTypeFilter] = Field(None, description="文件类型筛选")


# 🆕 用户信息模型
class UserInfoResponse(BaseModel):
    """用户信息响应模型"""
    user_id: int
    username: str
    nickname: Optional[str] = None

    class Config:
        from_attributes = True


# 响应模型
class DocumentItemResponse(BaseModel):
    """文档条目响应模型"""
    id: int
    title: str
    summary: Optional[str]
    file_type: str
    user_id: int
    username: str = Field(..., description="用户名")  # 🆕 新增
    nickname: Optional[str] = Field(None, description="用户昵称")  # 🆕 新增
    publish_time: datetime
    view_count: int = 0
    is_featured: bool = False

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应模型"""
    documents: List[DocumentItemResponse]
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class DocumentDetailResponse(BaseModel):
    """文档详情响应模型"""
    id: int
    title: str
    content: Optional[str]
    summary: Optional[str]
    file_type: str
    file_path: Optional[str]
    user_id: int
    username: str = Field(..., description="用户名")  # 🆕 新增
    nickname: Optional[str] = Field(None, description="用户昵称")  # 🆕 新增
    publish_time: datetime
    view_count: int = 0
    is_featured: bool = False

    class Config:
        from_attributes = True


class CategoryStatsResponse(BaseModel):
    """分类统计响应模型"""
    md_count: int = Field(..., description="Markdown文档数量")
    pdf_count: int = Field(..., description="PDF文档数量")
    total_count: int = Field(..., description="总文档数量")


class HotDocumentsResponse(BaseModel):
    """热门文档响应模型"""
    documents: List[DocumentItemResponse]


class TechSquareStatsResponse(BaseModel):
    """技术广场统计响应模型"""
    total_documents: int = Field(..., description="总发布文档数")
    total_views: int = Field(..., description="总浏览量")
    today_published: int = Field(..., description="今日发布数")
    featured_count: int = Field(..., description="精选文档数")
    category_stats: CategoryStatsResponse

# 在文件末尾添加以下新的响应模型

class DocumentFileInfoResponse(BaseModel):
    """文档文件信息响应模型"""
    document_id: int
    title: str
    file_type: str
    file_size: int
    has_file: bool
    file_path: Optional[str]
    safe_filename: str
    file_exists: bool
    original_filename: Optional[str]
    actual_file_size: Optional[int] = 0
    mime_type: Optional[str]
    size_match: bool = False

    class Config:
        from_attributes = True


class FileAccessResponse(BaseModel):
    """文件访问通用响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None