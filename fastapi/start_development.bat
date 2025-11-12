@echo off
chcp 65001 >nul
echo 🚀 启动开发环境...
echo.

REM 设置环境变量
set ENVIRONMENT=development
echo ✅ 环境模式: %ENVIRONMENT%

REM 复制开发环境配置
if exist .env.development (
    copy /Y .env.development .env >nul
    echo ✅ 已加载开发环境配置
) else (
    echo ❌ 找不到 .env.development 文件
    pause
    exit /b 1
)

REM 启动开发服务器
echo.
echo 🔥 启动FastAPI开发服务器...
echo 📍 地址: http://localhost:8100
echo 📚 API文档: http://localhost:8100/docs
echo.
python -m app.main

pause