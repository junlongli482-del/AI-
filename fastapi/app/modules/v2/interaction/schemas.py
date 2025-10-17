from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# ============= 点赞相关 =============
class LikeResponse(BaseModel):
    """点赞响应模型"""
    success: bool
    message: str
    is_liked: bool
    like_count: int


class LikeStatusResponse(BaseModel):
    """点赞状态响应模型"""
    is_liked: bool
    like_count: int


# ============= 收藏相关 =============
class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    success: bool
    message: str
    is_favorited: bool
    favorite_count: int


class FavoriteStatusResponse(BaseModel):
    """收藏状态响应模型"""
    is_favorited: bool
    favorite_count: int


class FavoriteItem(BaseModel):
    """收藏项模型"""
    id: int
    document_id: int
    document_title: str
    document_summary: Optional[str]
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """收藏列表响应模型"""
    items: List[FavoriteItem]
    total: int
    page: int
    size: int
    pages: int


# ============= 评论相关 =============
class CommentCreate(BaseModel):
    """创建评论请求模型"""
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID（回复时使用）")

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('评论内容不能为空')
        return v.strip()


class CommentUpdate(BaseModel):
    """更新评论请求模型"""
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('评论内容不能为空')
        return v.strip()


class CommentUser(BaseModel):
    """评论用户信息"""
    id: int
    username: str
    nickname: Optional[str]

    class Config:
        from_attributes = True


class CommentReply(BaseModel):
    """评论回复模型"""
    id: int
    content: str
    user: CommentUser
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentItem(BaseModel):
    """评论项模型"""
    id: int
    content: str
    user: CommentUser
    replies: List[CommentReply] = []
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """评论列表响应模型"""
    items: List[CommentItem]
    total: int
    page: int
    size: int
    pages: int


class CommentResponse(BaseModel):
    """评论操作响应模型"""
    success: bool
    message: str
    comment: Optional[CommentItem] = None


# ============= 统计相关 =============
class InteractionStats(BaseModel):
    """互动统计模型"""
    document_id: int
    like_count: int
    favorite_count: int
    comment_count: int
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInteractionStats(BaseModel):
    """用户互动统计模型"""
    total_likes_given: int
    total_favorites: int
    total_comments: int
    total_likes_received: int
    total_favorites_received: int
    total_comments_received: int