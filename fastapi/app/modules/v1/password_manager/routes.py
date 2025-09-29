"""
密码管理模块 - API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from .schemas import (
    PasswordChangeRequest,
    PasswordChangeResponse,
    PasswordStrengthCheck,
    PasswordStrengthResponse,
    ModuleTestResponse
)
from .services import PasswordService
from .dependencies import get_current_user_id, get_password_service

# 创建路由器
router = APIRouter()


@router.post(
    "/change-password",
    response_model=PasswordChangeResponse,
    summary="修改密码",
    description="用户修改密码，需要验证原密码"
)
async def change_password(
        request: PasswordChangeRequest,
        current_user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db),
        password_service: PasswordService = Depends(get_password_service)
):
    """
    修改用户密码

    - **current_password**: 当前密码
    - **new_password**: 新密码（最少8位，包含字母和数字）
    - **confirm_password**: 确认新密码
    """
    try:
        # 调用密码修改服务
        success, message = password_service.change_password(
            db=db,
            user_id=current_user_id,
            current_password=request.current_password,
            new_password=request.new_password
        )

        if success:
            # 获取用户基本信息
            user = password_service.get_user_by_id(db, current_user_id)
            user_info = {
                "id": user.id,
                "username": user.username,
                "display_name": user.nickname if user.nickname else user.username
            }

            return PasswordChangeResponse(
                message=message,
                success=True,
                user_info=user_info
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码修改失败：{str(e)}"
        )


@router.post(
    "/check-strength",
    response_model=PasswordStrengthResponse,
    summary="检查密码强度",
    description="检查密码强度并提供改进建议"
)
async def check_password_strength(
        request: PasswordStrengthCheck,
        password_service: PasswordService = Depends(get_password_service)
):
    """
    检查密码强度

    - **password**: 要检查的密码

    返回密码强度等级和改进建议
    """
    try:
        strength_info = password_service.check_password_strength(request.password)

        return PasswordStrengthResponse(
            is_valid=strength_info["is_valid"],
            strength_level=strength_info["strength_level"],
            requirements=strength_info["requirements"],
            suggestions=strength_info["suggestions"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码强度检查失败：{str(e)}"
        )


@router.get(
    "/test",
    response_model=ModuleTestResponse,
    summary="模块测试",
    description="测试密码管理模块是否正常运行"
)
async def test_module(db: Session = Depends(get_db)):
    """
    测试密码管理模块

    返回模块运行状态和基本信息
    """
    try:
        # 测试数据库连接
        from sqlalchemy import text
        result = db.execute(text("SELECT COUNT(*) as count FROM us_users"))
        user_count = result.fetchone().count

        # 模块端点列表
        endpoints = [
            "POST /change-password - 修改密码",
            "POST /check-strength - 检查密码强度",
            "GET /test - 模块测试"
        ]

        return ModuleTestResponse(
            message="密码管理模块正常运行",
            module="password_manager",
            version="v1",
            endpoints=endpoints,
            database_status=f"正常 (用户总数: {user_count})"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模块测试失败：{str(e)}"
        )


@router.get(
    "/user-info",
    summary="获取当前用户信息",
    description="获取当前登录用户的基本信息（用于密码修改页面显示）"
)
async def get_current_user_info(
        current_user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db),
        password_service: PasswordService = Depends(get_password_service)
):
    """
    获取当前用户基本信息

    用于在密码修改页面显示用户信息
    """
    try:
        user = password_service.get_user_by_id(db, current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.nickname if user.nickname else user.username,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败：{str(e)}"
        )