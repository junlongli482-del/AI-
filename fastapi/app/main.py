from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import importlib
from .core.database import engine, Base

# 导入所有模型（确保表能被创建）
def import_models():
    """导入所有模型以确保表能被正确创建"""
    try:
        from .modules.v1.user_register.models import User
        print("✅ 用户模型导入成功")
    except Exception as e:
        print(f"❌ 用户模型导入失败: {e}")

# 导入模型
import_models()

# 创建所有数据库表
Base.metadata.create_all(bind=engine)
print("✅ 数据库表创建完成")

app = FastAPI(
    title="用户系统API",
    description="模块化的用户管理系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
                print(f"🔍 扫描版本: {version_dir}")

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
                                print(f"  ✅ 已注册模块: {version_dir}/{module_name}")
                        except Exception as e:
                            print(f"  ❌ 注册模块 {version_dir}/{module_name} 失败: {e}")


# 注册所有模块
register_modules()


@app.get("/")
async def root():
    return {"message": "用户系统API正在运行", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)