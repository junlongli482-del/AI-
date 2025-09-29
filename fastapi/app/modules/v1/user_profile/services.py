"""
用户中心模块 - 业务逻辑服务
处理用户资料相关的所有业务逻辑
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

from .models import User
from .schemas import (
    UserProfileResponse,
    UserBasicInfoResponse,
    UpdateNicknameRequest,
    UserProfileUpdateResponse
)

# 配置日志
logger = logging.getLogger(__name__)


class UserProfileService:
    """
    用户中心服务类
    处理用户资料相关的所有业务操作
    """

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_user_profile(self, user_id: int) -> UserProfileResponse:
        """
        获取用户完整资料

        Args:
            user_id: 用户ID

        Returns:
            UserProfileResponse: 用户完整资料

        Raises:
            HTTPException: 用户不存在时抛出404错误
        """
        try:
            # 查询用户信息
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"用户不存在: user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )

            # 构建响应数据
            profile_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "display_name": user.get_display_name(),
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }

            logger.info(f"获取用户资料成功: user_id={user_id}")
            return UserProfileResponse(**profile_data)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户资料失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户资料失败"
            )

    def update_nickname(self, user_id: int, request: UpdateNicknameRequest) -> UserProfileUpdateResponse:
        """
        更新用户昵称

        Args:
            user_id: 用户ID
            request: 昵称更新请求

        Returns:
            UserProfileUpdateResponse: 更新结果

        Raises:
            HTTPException: 各种业务异常
        """
        try:
            # 查询用户
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"用户不存在: user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )

            # 检查用户是否激活
            if not user.is_active:
                logger.warning(f"用户账户已被禁用: user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户账户已被禁用"
                )

            new_nickname = request.nickname
            old_nickname = user.nickname

            # 如果昵称没有变化，直接返回
            if new_nickname == old_nickname:
                logger.info(f"昵称无变化: user_id={user_id}, nickname={new_nickname}")
                return self._build_update_response(user, "昵称无需更新")

            # 如果新昵称不为空，检查唯一性
            if new_nickname:
                existing_user = self.db.query(User).filter(
                    User.nickname == new_nickname,
                    User.id != user_id
                ).first()

                if existing_user:
                    logger.warning(f"昵称已被使用: nickname={new_nickname}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="该昵称已被其他用户使用"
                    )

            # 更新昵称
            user.nickname = new_nickname
            self.db.commit()
            self.db.refresh(user)

            # 记录日志
            action = "清空昵称" if new_nickname is None else f"更新昵称为: {new_nickname}"
            logger.info(f"昵称更新成功: user_id={user_id}, action={action}")

            # 构建响应
            message = "昵称已清空" if new_nickname is None else "昵称更新成功"
            return self._build_update_response(user, message)

        except HTTPException:
            raise
        except IntegrityError as e:
            # 数据库约束错误（昵称重复）
            self.db.rollback()
            logger.error(f"昵称唯一性约束错误: user_id={user_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该昵称已被其他用户使用"
            )
        except Exception as e:
            # 其他未知错误
            self.db.rollback()
            logger.error(f"更新昵称失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新昵称失败"
            )

    def check_nickname_availability(self, nickname: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        检查昵称是否可用

        Args:
            nickname: 要检查的昵称
            exclude_user_id: 排除的用户ID（用于更新时排除自己）

        Returns:
            bool: True表示可用，False表示已被使用
        """
        try:
            if not nickname:
                return True  # 空昵称总是可用的

            query = self.db.query(User).filter(User.nickname == nickname)

            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)

            existing_user = query.first()
            return existing_user is None

        except Exception as e:
            logger.error(f"检查昵称可用性失败: nickname={nickname}, error={str(e)}")
            return False

    def get_user_basic_info(self, user_id: int) -> UserBasicInfoResponse:
        """
        获取用户基本信息（简化版）

        Args:
            user_id: 用户ID

        Returns:
            UserBasicInfoResponse: 用户基本信息
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )

            return UserBasicInfoResponse(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                display_name=user.get_display_name()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户基本信息失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户信息失败"
            )

    def _build_update_response(self, user: User, message: str) -> UserProfileUpdateResponse:
        """
        构建更新响应

        Args:
            user: 用户对象
            message: 响应消息

        Returns:
            UserProfileUpdateResponse: 更新响应
        """
        user_info = UserBasicInfoResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            display_name=user.get_display_name()
        )

        return UserProfileUpdateResponse(
            message=message,
            success=True,
            user=user_info
        )

    def get_module_status(self) -> Dict[str, Any]:
        """
        获取模块状态信息（用于测试接口）

        Returns:
            Dict: 模块状态信息
        """
        try:
            # 测试数据库连接
            user_count = self.db.query(User).count()

            return {
                "message": "用户中心模块正常运行",
                "module": "user_profile",
                "version": "v1",
                "endpoints": [
                    "GET /api/v1/user_profile/me - 获取用户资料",
                    "PUT /api/v1/user_profile/nickname - 更新昵称",
                    "POST /api/v1/user_profile/logout - 退出登录",
                    "GET /api/v1/user_profile/test - 模块测试"
                ],
                "database_status": f"正常 (用户总数: {user_count})"
            }

        except Exception as e:
            logger.error(f"获取模块状态失败: error={str(e)}")
            return {
                "message": "用户中心模块运行异常",
                "module": "user_profile",
                "version": "v1",
                "endpoints": [],
                "database_status": f"异常: {str(e)}"
            }