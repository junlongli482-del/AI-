@echo off
chcp 65001 >nul
title 启动项目
echo 启动文档管理系统...
echo.

echo [1/3] 激活Python环境...
call conda activate xm3

echo [2/3] 启动后端服务 (4进程)...
cd /d "%~dp0fastapi"
start "API-8100" cmd /k conda activate xm3 ^&^& uvicorn app.main:app --host 127.0.0.1 --port 8100
timeout /t 2 >nul
start "API-8101" cmd /k conda activate xm3 ^&^& uvicorn app.main:app --host 127.0.0.1 --port 8101
timeout /t 2 >nul
start "API-8102" cmd /k conda activate xm3 ^&^& uvicorn app.main:app --host 127.0.0.1 --port 8102
timeout /t 2 >nul
start "API-8103" cmd /k conda activate xm3 ^&^& uvicorn app.main:app --host 127.0.0.1 --port 8103

echo [3/3] 启动Nginx...
cd /d "%~dp0nginx"
start nginx.exe

echo.
echo ✅ 启动完成！访问: http://localhost
pause