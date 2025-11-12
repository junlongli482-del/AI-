from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os
import importlib
import logging
from .core.config import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# 🔧 修复：将初始化代码移到函数中，只在应用启动时执行一次
def create_app() -> FastAPI:
    """创建FastAPI应用实例"""

    # 导入数据库相关（只在应用创建时导入一次）
    from .core.database import engine, Base

    # 导入所有模型（确保表能被创建）
    def import_models():
        """导入所有模型以确保表能被正确创建"""
        try:
            from .modules.v1.user_register.models import User
            logger.info("✅ 用户模型导入成功")
        except Exception as e:
            logger.error(f"❌ 用户模型导入失败: {e}")

    # 导入模型（只执行一次）
    import_models()

    # 创建所有数据库表（只执行一次）
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库表创建完成")

    # 创建FastAPI应用
    app = FastAPI(
        title="用户系统API",
        description="模块化的用户管理系统",
        version="2.0.0",
        debug=settings.DEBUG,
        docs_url="/docs" if settings.is_development else None,  # 生产环境关闭文档
        redoc_url="/redoc" if settings.is_development else None
    )

    # 添加中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)  # Gzip压缩

    # 配置CORS
    if settings.is_development:
        # 开发环境：允许所有来源
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # 生产环境：限制来源
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost", "http://localhost:80"],  # 根据实际情况修改
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

    # 自动发现并注册模块路由（支持版本化）
    def register_modules():
        modules_path = os.path.join(os.path.dirname(__file__), "modules")
        if os.path.exists(modules_path):
            # 遍历版本目录
            for version_dir in os.listdir(modules_path):
                version_path = os.path.join(modules_path, version_dir)
                if os.path.isdir(version_path) and not version_dir.startswith("__"):
                    logger.info(f"🔍 扫描版本: {version_dir}")

                    # 遍历版本下的模块
                    for module_name in os.listdir(version_path):
                        module_path = os.path.join(version_path, module_name)
                        if os.path.isdir(module_path) and not module_name.startswith("__"):
                            try:
                                # 动态导入模块的路由
                                module = importlib.import_module(f"app.modules.{version_dir}.{module_name}.routes")
                                if hasattr(module, "router"):
                                    app.include_router(
                                        module.router,
                                        prefix=f"/api/{version_dir}/{module_name}",
                                        tags=[f"{version_dir}-{module_name}"]
                                    )
                                    logger.info(f"  ✅ 已注册模块: {version_dir}/{module_name}")
                            except Exception as e:
                                logger.error(f"  ❌ 注册模块 {version_dir}/{module_name} 失败: {e}")

    # 注册所有模块（只执行一次）
    register_modules()

    # 定义路由
    @app.get("/")
    async def root():
        return {
            "message": "用户系统API正在运行",
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT
        }

    @app.get("/api/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }

    return app


# 🔧 修复：创建应用实例（只创建一次）
app = create_app()

if __name__ == "__main__":
    import uvicorn

    if settings.is_development:
        # 开发模式：单进程 + 热重载
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level=settings.LOG_LEVEL.lower()
        )
    else:
        # 生产模式：单进程（Gunicorn会覆盖）
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            log_level=settings.LOG_LEVEL.lower()
        )