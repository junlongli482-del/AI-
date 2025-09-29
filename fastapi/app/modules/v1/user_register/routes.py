from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import UserRegisterRequest, UserRegisterResponse, ErrorResponse
from .services import UserRegisterService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账号"
)
async def register_user(
        user_data: UserRegisterRequest,
        db: Session = Depends(get_db)
):
    """
    用户注册接口

    - **username**: 用户名（3-20字符，只能包含字母数字）
    - **email**: 邮箱地址
    - **password**: 密码（至少8位，包含字母和数字）
    """
    try:
        # 检查用户名和邮箱唯一性
        if UserRegisterService.check_username_exists(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        if UserRegisterService.check_email_exists(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )

        # 创建用户
        new_user = UserRegisterService.create_user(db, user_data)

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.get("/test")
async def test_register_module():
    """测试注册模块是否正常工作"""
    return {"message": "用户注册模块正常运行", "module": "user_register", "version": "v1"}