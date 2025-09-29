"""
用户认证模块 - API数据模型
定义登录请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求模型"""
    username_or_email: str = Field(..., min_length=3, max_length=100, description="用户名或邮箱")
    password: str = Field(..., min_length=8, max_length=50, description="密码")
    remember_me: Optional[bool] = Field(False, description="记住登录状态")

    class Config:
        json_schema_extra = {
            "example": {
                "username_or_email": "alice",
                "password": "password123",
                "remember_me": False
            }
        }


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserInfo(BaseModel):
    """用户信息模型"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "alice",
                "email": "alice@example.com",
                "is_active": True,
                "created_at": "2025-01-20T10:30:00"
            }
        }