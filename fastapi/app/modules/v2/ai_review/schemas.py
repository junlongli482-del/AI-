from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ReviewType(str, Enum):
    content_quality = "content_quality"
    content_safety = "content_safety"
    format_check = "format_check"
    length_check = "length_check"

class ReviewResult(str, Enum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    error = "error"

class RuleType(str, Enum):
    length_limit = "length_limit"
    format_check = "format_check"
    content_policy = "content_policy"
    quality_standard = "quality_standard"

# 提交审核请求
class ReviewSubmitRequest(BaseModel):
    document_id: int = Field(..., description="文档ID")
    review_types: List[ReviewType] = Field(default=[ReviewType.content_safety], description="审核类型列表")
    priority: Optional[int] = Field(default=1, description="审核优先级")

# 审核结果响应
class ReviewLogResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    review_type: ReviewType
    ai_provider: str
    file_id: Optional[str]
    review_result: ReviewResult
    failure_reason: Optional[str]
    confidence_score: Optional[float]
    review_duration: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 审核状态查询响应
class ReviewStatusResponse(BaseModel):
    document_id: int
    overall_status: ReviewResult
    review_logs: List[ReviewLogResponse]
    total_reviews: int
    passed_reviews: int
    failed_reviews: int
    pending_reviews: int

# 审核历史查询请求
class ReviewHistoryRequest(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    review_type: Optional[ReviewType] = Field(default=None, description="筛选审核类型")
    review_result: Optional[ReviewResult] = Field(default=None, description="筛选审核结果")

# 审核规则相关
class ReviewRuleCreate(BaseModel):
    rule_name: str = Field(..., max_length=100, description="规则名称")
    rule_type: RuleType = Field(..., description="规则类型")
    rule_config: Dict[str, Any] = Field(..., description="规则配置")
    is_active: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=1, description="优先级")

class ReviewRuleResponse(BaseModel):
    id: int
    rule_name: str
    rule_type: RuleType
    rule_config: Dict[str, Any]
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 审核统计响应
class ReviewStatsResponse(BaseModel):
    total_reviews: int
    today_reviews: int
    passed_rate: float
    failed_rate: float
    avg_review_duration: Optional[float]
    review_type_stats: Dict[str, int]
    recent_reviews: List[ReviewLogResponse]