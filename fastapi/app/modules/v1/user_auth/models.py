"""
用户认证模块 - 数据模型
复用用户注册模块的User模型，无需重复定义
"""

# 从用户注册模块导入User模型
from app.modules.v1.user_register.models import User

# 导出给其他模块使用
__all__ = ["User"]