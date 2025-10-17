from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SessionType(str, Enum):
    NEW_DOCUMENT = "new_document"
    EDIT_DOCUMENT = "edit_document"

class OptimizationStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

# 请求模型
class CreateSessionRequest(BaseModel):
    document_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    session_type: SessionType = SessionType.NEW_DOCUMENT

class UpdateSessionRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    is_draft: Optional[bool] = None

class OptimizeContentRequest(BaseModel):
    content: str = Field(..., min_length=1, description="要优化的MD内容")
    optimization_type: Optional[str] = Field("general", description="优化类型：general, grammar, structure, expand")

class SaveDocumentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    folder_id: Optional[int] = None
    summary: Optional[str] = Field(None, max_length=500)

# 响应模型
class AIOptimizationResponse(BaseModel):
    id: int
    original_content: str
    optimized_content: str
    optimization_prompt: Optional[str]
    ai_provider: str
    status: OptimizationStatus
    created_at: datetime

    class Config:
        from_attributes = True

class EditorSessionResponse(BaseModel):
    id: int
    document_id: Optional[int]
    title: Optional[str]
    content: Optional[str]
    is_draft: bool
    session_type: SessionType
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EditorSessionDetailResponse(EditorSessionResponse):
    ai_optimizations: List[AIOptimizationResponse] = []

class OptimizeResponse(BaseModel):
    success: bool
    message: str
    optimization_id: int
    original_content: str
    optimized_content: str
    can_apply: bool = True

class EditorStatsResponse(BaseModel):
    total_sessions: int
    draft_sessions: int
    total_optimizations: int
    recent_sessions: List[EditorSessionResponse]