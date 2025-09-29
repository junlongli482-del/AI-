"""
密码管理模块 - API数据结构定义
"""

from pydantic import BaseModel, Field, validator
import re
from typing import Optional


class PasswordChangeRequest(BaseModel):
    """修改密码请求模型"""
    current_password: str = Field(
        ...,
        min_length=1,
        description="当前密码"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="新密码，最少8位，必须包含字母和数字"
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="确认新密码"
    )

    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')

        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')

        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')

        # 可选：检查特殊字符
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        #     raise ValueError('密码必须包含至少一个特殊字符')

        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证两次密码输入一致"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v


class PasswordChangeResponse(BaseModel):
    """修改密码响应模型"""
    message: str = Field(description="操作结果消息")
    success: bool = Field(description="操作是否成功")
    user_info: Optional[dict] = Field(default=None, description="用户基本信息")


class PasswordStrengthCheck(BaseModel):
    """密码强度检查请求模型"""
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="要检查的密码"
    )


class PasswordStrengthResponse(BaseModel):
    """密码强度检查响应模型"""
    is_valid: bool = Field(description="密码是否符合要求")
    strength_level: str = Field(description="密码强度等级：弱/中/强")
    requirements: dict = Field(description="密码要求检查结果")
    suggestions: list = Field(default=[], description="改进建议")


class ModuleTestResponse(BaseModel):
    """模块测试响应模型"""
    message: str
    module: str
    version: str
    endpoints: list
    database_status: str