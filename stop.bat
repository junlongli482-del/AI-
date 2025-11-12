@echo off
chcp 65001 >nul
title 停止项目
echo 停止所有服务...

taskkill /f /im nginx.exe >nul 2>&1
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo table /nh ^| findstr uvicorn') do taskkill /f /pid %%i >nul 2>&1

echo ✅ 已停止
pause