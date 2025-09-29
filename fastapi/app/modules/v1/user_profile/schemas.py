"""
用户中心模块 - API数据模型
定义用户中心相关的请求和响应数据结构
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


# ==================== 响应模型 ====================

class UserProfileResponse(BaseModel):
    """
    用户资料响应模型
    用于返回用户的完整资料信息
    """
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名（不可修改）")
    email: str = Field(..., description="邮箱（不可修改）")
    nickname: Optional[str] = Field(None, description="昵称（可修改）")
    display_name: str = Field(..., description="显示名称（昵称优先，否则用户名）")
    is_active: bool = Field(..., description="账户状态")
    created_at: datetime = Field(..., description="注册时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True  # 支持从SQLAlchemy模型转换
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }


class UserBasicInfoResponse(BaseModel):
    """
    用户基本信息响应模型
    用于返回用户的基本信息（简化版）
    """
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    display_name: str = Field(..., description="显示名称")

    class Config:
        from_attributes = True


# ==================== 请求模型 ====================

class UpdateNicknameRequest(BaseModel):
    """
    更新昵称请求模型
    """
    nickname: Optional[str] = Field(
        None,
        min_length=2,
        max_length=20,
        description="用户昵称，2-20个字符，支持中英文数字"
    )

    @validator('nickname')
    def validate_nickname(cls, v):
        """
        昵称验证器
        """
        if v is None:
            return v

        # 去除首尾空格
        v = v.strip()

        # 如果处理后为空字符串，返回None
        if not v:
            return None

        # 长度检查
        if len(v) < 2 or len(v) > 20:
            raise ValueError('昵称长度必须在2-20个字符之间')

        # 字符检查：只允许中文、英文、数字
        pattern = r'^[一-龥a-zA-Z0-9]+$'
        if not re.match(pattern, v):
            raise ValueError('昵称只能包含中文、英文字母和数字')

        # 不能全是数字
        if v.isdigit():
            raise ValueError('昵称不能全是数字')

        return v


# ==================== 通用响应模型 ====================

class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str = Field(..., description="响应消息")
    success: bool = Field(True, description="操作是否成功")


class UserProfileUpdateResponse(BaseModel):
    """
    用户资料更新响应模型
    """
    message: str = Field(..., description="更新结果消息")
    success: bool = Field(..., description="更新是否成功")
    user: UserBasicInfoResponse = Field(..., description="更新后的用户信息")


# ==================== 模块测试响应模型 ====================

class ModuleTestResponse(BaseModel):
    """
    模块测试响应模型
    """
    message: str = Field(..., description="测试消息")
    module: str = Field(..., description="模块名称")
    version: str = Field(..., description="版本号")
    endpoints: list = Field(..., description="可用端点列表")
    database_status: str = Field(..., description="数据库连接状态")