"""
用户中心模块 - 数据模型
复用用户注册模块的User模型，扩展昵称字段支持
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    用户模型 - 扩展版本
    包含昵称字段支持
    """
    __tablename__ = "us_users"

    # 基础字段
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")

    # 新增昵称字段
    nickname = Column(String(50), unique=True, index=True, nullable=True, comment="用户昵称")

    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 时间字段
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def get_display_name(self) -> str:
        """
        获取显示名称
        优先显示昵称，如果没有昵称则显示用户名
        """
        return self.nickname if self.nickname else self.username

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"