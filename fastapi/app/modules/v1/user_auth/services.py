"""
用户认证模块 - 业务逻辑
处理用户登录、JWT令牌生成和验证等核心功能
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.core.database import get_db
from .models import User
from .schemas import LoginRequest, TokenResponse, UserInfo


class AuthService:
    """认证服务类"""

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """
        验证密码
        Args:
            plain_password: 明文密码
            password_hash: 存储的密码哈希（格式：盐值:哈希值）
        Returns:
            bool: 密码是否正确
        """
        try:
            # 分离盐值和哈希值
            salt, stored_hash = password_hash.split(':')
            # 使用相同的盐值计算哈希
            calculated_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
            return calculated_hash == stored_hash
        except ValueError:
            return False

    @staticmethod
    def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
        """
        验证用户身份
        Args:
            db: 数据库会话
            username_or_email: 用户名或邮箱
            password: 密码
        Returns:
            User: 验证成功返回用户对象，失败返回None
        """
        # 查找用户（支持用户名或邮箱登录）
        user = db.query(User).filter(
            or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()

        # 用户不存在
        if not user:
            return None

        # 用户被禁用
        if not user.is_active:
            return None

        # 验证密码
        if not AuthService.verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
        Returns:
            str: JWT令牌
        """
        to_encode = data.copy()

        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        # 生成JWT令牌
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        创建刷新令牌
        Args:
            data: 要编码的数据
        Returns:
            str: 刷新令牌
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        验证令牌
        Args:
            token: JWT令牌
        Returns:
            dict: 令牌载荷，验证失败返回None
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def login_user(db: Session, login_data: LoginRequest) -> Optional[TokenResponse]:
        """
        用户登录
        Args:
            db: 数据库会话
            login_data: 登录请求数据
        Returns:
            TokenResponse: 登录成功返回令牌信息，失败返回None
        """
        # 验证用户身份
        user = AuthService.authenticate_user(
            db,
            login_data.username_or_email,
            login_data.password
        )

        if not user:
            return None

        # 准备令牌数据
        token_data = {
            "sub": str(user.id),  # subject: 用户ID
            "username": user.username,
            "email": user.email
        }

        # 创建访问令牌
        access_token = AuthService.create_access_token(data=token_data)

        # 如果选择记住登录，创建刷新令牌
        refresh_token = None
        if login_data.remember_me:
            refresh_token = AuthService.create_refresh_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒
        )

    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        根据令牌获取当前用户
        Args:
            db: 数据库会话
            token: JWT令牌
        Returns:
            User: 用户对象，验证失败返回None
        """
        # 验证令牌
        payload = AuthService.verify_token(token)
        if not payload:
            return None

        # 获取用户ID
        user_id = payload.get("sub")
        if not user_id:
            return None

        # 查询用户
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user