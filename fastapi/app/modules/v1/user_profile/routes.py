"""
用户中心模块 - API路由
定义用户中心相关的所有API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

# 导入核心依赖
from ....core.database import get_db
from ..user_auth.dependencies import get_current_active_user

# 导入本模块组件
from .services import UserProfileService
from .schemas import (
    UserProfileResponse,
    UpdateNicknameRequest,
    UserProfileUpdateResponse,
    MessageResponse,
    ModuleTestResponse
)
from .dependencies import get_user_profile_service

# 创建路由器
router = APIRouter(
    # prefix="/user_profile",
    # tags=["用户中心"],
    responses={
        401: {"description": "未授权访问"},
        403: {"description": "权限不足"},
        404: {"description": "资源不存在"},
        500: {"description": "服务器内部错误"}
    }
)

@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="获取用户资料",
    description="获取当前登录用户的完整资料信息，包括用户名、邮箱、昵称等"
)
async def get_my_profile(
    current_user = Depends(get_current_active_user),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """
    获取当前用户的完整资料

    - **需要登录**：需要在请求头中提供有效的JWT令牌
    - **返回信息**：用户ID、用户名、邮箱、昵称、显示名称、账户状态、注册时间等
    - **显示名称逻辑**：优先显示昵称，如果没有昵称则显示用户名
    """
    return service.get_user_profile(current_user.id)

@router.put(
    "/nickname",
    response_model=UserProfileUpdateResponse,
    summary="更新用户昵称",
    description="更新当前用户的昵称，支持设置新昵称或清空昵称"
)
async def update_my_nickname(
    request: UpdateNicknameRequest,
    current_user = Depends(get_current_active_user),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """
    更新当前用户的昵称

    - **需要登录**：需要在请求头中提供有效的JWT令牌
    - **昵称规则**：
      - 长度：2-20个字符
      - 字符：支持中文、英文字母、数字
      - 唯一性：不能与其他用户的昵称重复
      - 可以设置为null来清空昵称
    - **返回信息**：更新结果和最新的用户基本信息
    """
    return service.update_nickname(current_user.id, request)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="退出登录",
    description="退出当前用户的登录状态（前端需要清除本地存储的令牌）"
)
async def logout(
        current_user=Depends(get_current_active_user),
        service: UserProfileService = Depends(get_user_profile_service)
):
    """
    用户退出登录

    - **需要登录**：需要在请求头中提供有效的JWT令牌
    - **注意**：由于使用JWT无状态认证，服务端不维护会话状态
    - **前端处理**：收到成功响应后，前端需要清除本地存储的access_token和refresh_token
    - **安全建议**：如果需要立即失效令牌，建议实现令牌黑名单机制
    """
    try:
        # 通过服务获取完整的用户信息（包含nickname）
        user_profile = service.get_user_basic_info(current_user.id)
        display_name = user_profile.display_name
    except:
        # 如果获取失败，使用基础用户名
        display_name = current_user.username

    return MessageResponse(
        message=f"用户 {display_name} 已成功退出登录",
        success=True
    )
@router.get(
    "/check-nickname/{nickname}",
    response_model=Dict[str, Any],
    summary="检查昵称可用性",
    description="检查指定昵称是否可用（不需要登录）"
)
async def check_nickname_availability(
    nickname: str,
    service: UserProfileService = Depends(get_user_profile_service)
):
    """
    检查昵称是否可用

    - **无需登录**：公开接口，用于注册或修改昵称时的实时检查
    - **参数**：昵称字符串
    - **返回**：可用性状态和相关信息
    """
    # 先进行基本格式验证
    if len(nickname) < 2 or len(nickname) > 20:
        return {
            "available": False,
            "message": "昵称长度必须在2-20个字符之间",
            "nickname": nickname
        }

    # 检查字符格式
    import re
    pattern = r'^[一-\u9fa5a-zA-Z0-9]+$'
    if not re.match(pattern, nickname):
        return {
            "available": False,
            "message": "昵称只能包含中文、英文字母和数字",
            "nickname": nickname
        }

    # 不能全是数字
    if nickname.isdigit():
        return {
            "available": False,
            "message": "昵称不能全是数字",
            "nickname": nickname
        }

    # 检查唯一性
    is_available = service.check_nickname_availability(nickname)

    return {
        "available": is_available,
        "message": "昵称可用" if is_available else "昵称已被使用",
        "nickname": nickname
    }

@router.get(
    "/test",
    response_model=ModuleTestResponse,
    summary="模块测试接口",
    description="测试用户中心模块是否正常运行"
)
async def test_module(
    service: UserProfileService = Depends(get_user_profile_service)
):
    """
    测试用户中心模块

    - **无需登录**：公开测试接口
    - **功能**：检查模块状态、数据库连接、可用端点等
    - **用途**：开发调试和健康检查
    """
    status_info = service.get_module_status()
    return ModuleTestResponse(**status_info)

# 导出路由器
__all__ = ["router"]