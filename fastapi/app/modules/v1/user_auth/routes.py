"""
用户认证模块 - API路由
提供用户登录、令牌验证等API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import LoginRequest, TokenResponse, UserInfo
from .services import AuthService
from .dependencies import get_current_active_user
from .models import User

# 创建路由器
router = APIRouter(
    responses={404: {"description": "Not found"}}
)


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    用户登录接口

    支持两种登录方式：
    - 用户名 + 密码
    - 邮箱 + 密码

    Args:
        login_data: 登录请求数据
        db: 数据库会话

    Returns:
        TokenResponse: 包含访问令牌和刷新令牌的响应

    Raises:
        HTTPException: 登录失败时返回401错误
    """
    # 调用登录服务
    token_response = AuthService.login_user(db, login_data)

    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_response


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(
        current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的信息

    需要在请求头中提供有效的JWT令牌：
    Authorization: Bearer <your_token>

    Args:
        current_user: 当前登录用户（通过JWT令牌验证）

    Returns:
        UserInfo: 用户基本信息
    """
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/refresh", response_model=TokenResponse, summary="刷新访问令牌")
async def refresh_token(
        refresh_token: str,
        db: Session = Depends(get_db)
):
    """
    使用刷新令牌获取新的访问令牌

    Args:
        refresh_token: 刷新令牌
        db: 数据库会话

    Returns:
        TokenResponse: 新的访问令牌

    Raises:
        HTTPException: 刷新令牌无效时返回401错误
    """
    # 验证刷新令牌
    payload = AuthService.verify_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    # 获取用户ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    # 查询用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 生成新的访问令牌
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email
    }

    new_access_token = AuthService.create_access_token(data=token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_token,  # 刷新令牌保持不变
        token_type="bearer",
        expires_in=30 * 60  # 30分钟
    )


@router.get("/test", summary="模块测试接口")
async def test_module():
    """
    测试用户认证模块是否正常运行

    Returns:
        dict: 模块状态信息
    """
    return {
        "message": "用户认证模块正常运行",
        "module": "user_auth",
        "version": "v1",
        "endpoints": [
            "POST /api/v1/user_auth/login - 用户登录",
            "GET /api/v1/user_auth/me - 获取当前用户信息",
            "POST /api/v1/user_auth/refresh - 刷新令牌",
            "GET /api/v1/user_auth/test - 模块测试"
        ]
    }