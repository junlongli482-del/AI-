"""
密码管理模块 - 数据模型

复用现有的User模型，不需要新的数据表
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    用户模型 - 复用现有表结构

    注意：这里只是为了类型提示和IDE支持
    实际使用的是 user_register 模块中的User模型
    """
    __tablename__ = "us_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # 格式：盐值:哈希值
    nickname = Column(String(50), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"