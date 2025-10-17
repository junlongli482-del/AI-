"""
文件上传模块 - API验证模型
功能：定义请求和响应的数据结构
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileTypeEnum(str, Enum):
    """文件类型枚举"""
    MD = "md"
    PDF = "pdf"


class FileStatusEnum(str, Enum):
    """文件状态枚举"""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    FAILED = "failed"
    DELETED = "deleted"


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool = Field(..., description="上传是否成功")
    message: str = Field(..., description="响应消息")
    upload_id: Optional[int] = Field(None, description="上传记录ID")
    file_info: Optional[dict] = Field(None, description="文件信息")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileValidationResponse(BaseModel):
    """文件验证响应模型"""
    is_valid: bool = Field(..., description="文件是否有效")
    file_type: str = Field(..., description="检测到的文件类型")  # 🔧 改为字符串
    file_size: int = Field(..., description="文件大小(字节)")
    validation_details: dict = Field(..., description="验证详情")
    error_message: Optional[str] = Field(None, description="错误信息")


class UploadRecordResponse(BaseModel):
    """上传记录响应模型"""
    id: int
    original_filename: str
    file_size: int
    file_type: str  # 🔧 改为字符串
    status: str     # 🔧 改为字符串
    validation_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileListResponse(BaseModel):
    """文件列表响应模型"""
    files: List[UploadRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FileUploadConfig(BaseModel):
    """文件上传配置模型"""
    max_file_size_mb: int = Field(default=50, description="最大文件大小(MB)")
    allowed_extensions: List[str] = Field(default=[".md", ".pdf"], description="允许的文件扩展名")
    upload_path: str = Field(default="uploads", description="上传路径")

    @validator('max_file_size_mb')
    def validate_max_size(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('文件大小限制必须在1-100MB之间')
        return v


class CreateDocumentFromUploadRequest(BaseModel):
    """从上传文件创建文档的请求模型"""
    upload_id: int = Field(..., description="上传记录ID")
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    summary: Optional[str] = Field(None, max_length=500, description="文档摘要")
    folder_id: Optional[int] = Field(None, description="文件夹ID")

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('文档标题不能为空')
        return v.strip()