"""
文档管理模块 - 数据验证模型
功能：定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileTypeEnum(str, Enum):
    """文件类型枚举"""
    MD = "md"
    PDF = "pdf"


class DocumentStatusEnum(str, Enum):
    """文档状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    REVIEW_FAILED = "review_failed"


# ==================== 文件夹相关 ====================

class FolderCreateRequest(BaseModel):
    """创建文件夹请求"""
    name: str = Field(..., min_length=1, max_length=100, description="文件夹名称")
    parent_id: Optional[int] = Field(None, description="父文件夹ID，不填表示根目录")

    @validator('name')
    def validate_name(cls, v):
        # 文件夹名称不能包含特殊字符
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in forbidden_chars):
            raise ValueError('文件夹名称不能包含特殊字符：/ \\ : * ? " < > |')
        return v.strip()


class FolderResponse(BaseModel):
    """文件夹响应"""
    id: int
    name: str
    parent_id: Optional[int]
    level: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FolderTreeResponse(BaseModel):
    """文件夹树形结构响应"""
    id: int
    name: str
    level: int
    children: List['FolderTreeResponse'] = []
    document_count: int = 0  # 该文件夹下的文档数量

    class Config:
        from_attributes = True


# ==================== 文档相关 ====================

class DocumentCreateRequest(BaseModel):
    """创建文档请求"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容（MD格式）")
    summary: Optional[str] = Field(None, max_length=500, description="简短摘要")
    folder_id: Optional[int] = Field(None, description="所属文件夹ID")
    file_type: FileTypeEnum = Field(FileTypeEnum.MD, description="文件类型")


class DocumentUpdateRequest(BaseModel):
    """更新文档请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    summary: Optional[str] = Field(None, max_length=500, description="简短摘要")
    folder_id: Optional[int] = Field(None, description="所属文件夹ID")


class DocumentResponse(BaseModel):
    """文档响应"""
    id: int
    title: str
    content: Optional[str]
    file_path: Optional[str]
    file_type: FileTypeEnum
    file_size: int
    summary: Optional[str]
    status: DocumentStatusEnum
    publish_time: Optional[datetime]
    review_message: Optional[str]
    folder_id: Optional[int]
    folder_name: Optional[str] = None  # 文件夹名称（方便前端显示）
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    id: int
    title: str
    file_type: FileTypeEnum
    file_size: int
    status: DocumentStatusEnum
    folder_id: Optional[int]
    folder_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListWithPaginationResponse(BaseModel):
    """带分页的文档列表响应"""
    documents: List[DocumentListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== 通用响应 ====================

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    error_code: Optional[str] = None


# 解决循环引用问题
FolderTreeResponse.model_rebuild()