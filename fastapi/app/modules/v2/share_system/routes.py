from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from ....core.database import get_db
from ...v1.user_auth.dependencies import get_current_user
from .dependencies import get_optional_current_user  # 🆕 导入新依赖
from .services import share_system_service
from .schemas import (
    CreateShareRequest, UpdateShareRequest, AccessShareRequest,
    ShareResponse, ShareDetailResponse, ShareListResponse, ShareStatsResponse,
    PublicDocumentResponse
)

router = APIRouter()


@router.get("/test")
async def test_share_system():
    """测试分享系统接口连通性"""
    return {
        "message": "分享系统模块运行正常",
        "module": "share_system",
        "version": "v2",
        "status": "active"
    }


@router.post("/create", response_model=ShareResponse)
async def create_share(
    request: CreateShareRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建文档分享链接"""
    try:
        return share_system_service.create_share(request, current_user, db)
    except HTTPException as e:
        # 🔧 修复：直接重新抛出HTTPException
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分享失败: {str(e)}"
        )


@router.get("/my-shares", response_model=ShareListResponse)
async def get_my_shares(
        page: int = 1,
        size: int = 20,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取我的分享列表"""
    try:
        if page < 1 or size < 1 or size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="页码和每页数量必须为正数，且每页数量不超过100"
            )

        shares, total = share_system_service.get_my_shares(current_user, page, size, db)
        pages = (total + size - 1) // size

        return ShareListResponse(
            items=shares,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分享列表失败: {str(e)}"
        )


@router.get("/detail/{share_id}", response_model=ShareDetailResponse)
async def get_share_detail(
    share_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分享详情"""
    try:
        return share_system_service.get_share_detail(share_id, current_user, db)
    except HTTPException as e:
        # 🔧 修复：直接重新抛出HTTPException
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分享详情失败: {str(e)}"
        )

@router.put("/update/{share_id}", response_model=ShareResponse)
async def update_share(
        share_id: int,
        request: UpdateShareRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新分享配置"""
    try:
        return share_system_service.update_share(share_id, request, current_user, db)
    except Exception as e:
        if "不存在或无权限" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分享失败: {str(e)}"
        )


@router.delete("/delete/{share_id}")
async def delete_share(
        share_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除分享"""
    try:
        result = share_system_service.delete_share(share_id, current_user, db)
        return {"message": "分享删除成功"}
    except Exception as e:
        if "不存在或无权限" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分享失败: {str(e)}"
        )


# 🔧 修复：使用可选认证依赖
@router.post("/public/{share_code}", response_model=PublicDocumentResponse)
async def access_shared_document(
    share_code: str,
    request: AccessShareRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: Optional = Depends(get_optional_current_user)
):
    """访问分享的文档（公开接口）"""
    try:
        # 获取访问者信息
        visitor_ip = req.client.host
        visitor_user_agent = req.headers.get("user-agent", "")
        visitor_user_id = current_user.id if current_user else None

        return share_system_service.access_shared_document(
            share_code, request, visitor_ip, visitor_user_agent, visitor_user_id, db
        )
    except HTTPException as e:
        # 🔧 修复：直接重新抛出HTTPException，保持原有状态码
        raise e
    except Exception as e:
        # 🔧 修复：显示详细错误信息用于调试
        print(f"❌ 访问分享文档异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"访问分享文档失败: {str(e)}"
        )


# 🔧 修复：使用可选认证依赖
@router.get("/public/{share_code}")
async def get_shared_document(
        share_code: str,
        password: Optional[str] = None,
        req: Request = None,
        db: Session = Depends(get_db),
        current_user: Optional = Depends(get_optional_current_user)  # 🔧 使用新的可选依赖
):
    """获取分享的文档（GET方式，用于直接链接访问）"""
    try:
        # 构建请求对象
        access_request = AccessShareRequest(password=password)

        # 获取访问者信息
        visitor_ip = req.client.host
        visitor_user_agent = req.headers.get("user-agent", "")
        visitor_user_id = current_user.id if current_user else None

        return share_system_service.access_shared_document(
            share_code, access_request, visitor_ip, visitor_user_agent, visitor_user_id, db
        )
    except Exception as e:
        if "不存在" in str(e) or "失效" in str(e) or "过期" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "需要登录" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        elif "密码错误" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"访问分享文档失败: {str(e)}"
        )


# 🔧 修复：使用可选认证依赖
@router.get("/download/{share_code}")
async def download_shared_document(
        share_code: str,
        req: Request,
        db: Session = Depends(get_db),
        current_user: Optional = Depends(get_optional_current_user)  # 🔧 使用新的可选依赖
):
    """下载分享的文档"""
    try:
        # 获取访问者信息
        visitor_ip = req.client.host
        visitor_user_agent = req.headers.get("user-agent", "")
        visitor_user_id = current_user.id if current_user else None

        file_path, document_title = share_system_service.download_shared_document(
            share_code, visitor_ip, visitor_user_agent, visitor_user_id, db
        )

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )

        # 返回文件
        return FileResponse(
            path=file_path,
            filename=f"{document_title}.md",
            media_type='application/octet-stream'
        )
    except Exception as e:
        if "不存在" in str(e) or "不允许下载" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "不允许" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文档失败: {str(e)}"
        )


@router.get("/stats", response_model=ShareStatsResponse)
async def get_share_stats(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取分享统计"""
    try:
        return share_system_service.get_share_stats(current_user, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分享统计失败: {str(e)}"
        )


@router.post("/toggle-status/{share_id}")
async def toggle_share_status(
        share_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """切换分享状态（启用/禁用）"""
    try:
        # 获取当前分享
        share_detail = share_system_service.get_share_detail(share_id, current_user, db)

        # 切换状态
        new_status = "disabled" if share_detail.status == "active" else "active"
        update_request = UpdateShareRequest(status=new_status)

        updated_share = share_system_service.update_share(share_id, update_request, current_user, db)

        return {
            "message": f"分享状态已切换为{new_status}",
            "share": updated_share
        }
    except Exception as e:
        if "不存在或无权限" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换分享状态失败: {str(e)}"
        )


@router.get("/config")
async def get_share_config():
    """获取分享系统配置"""
    return {
        "share_types": [
            {"value": "public", "label": "公开分享", "description": "任何人都可以访问"},
            {"value": "private", "label": "私有分享", "description": "需要登录才能访问"},
            {"value": "password", "label": "密码保护", "description": "需要密码才能访问"}
        ],
        "max_expire_hours": 8760,  # 最大1年
        "default_expire_hours": 168,  # 默认7天
        "max_shares_per_document": 1,  # 每个文档最多1个活跃分享
        "supported_download_types": ["md", "pdf"],
        "base_share_url": "http://localhost:8100/api/v2/share_system/public/"
    }