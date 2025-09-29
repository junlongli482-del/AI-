from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20字符之间')
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if len(v) > 50:  # 添加最大长度限制
            raise ValueError('密码长度不能超过50位')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v


class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str