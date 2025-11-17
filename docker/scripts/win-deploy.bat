@echo off
title Docker Deploy Script

echo.
echo Docker Deploy - Vue3 + FastAPI Document Management System
echo ========================================================
echo.

REM Check Docker environment
echo [1/8] Checking Docker environment...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not installed
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose not installed
    pause
    exit /b 1
)
echo SUCCESS: Docker environment OK

REM Check frontend build
echo [2/8] Checking frontend build...
if not exist "..\vue3\dist\index.html" (
    echo WARNING: Frontend not built
    echo Please run: cd ..\vue3 ^&^& npm run build ^&^& cd ..\docker
    pause
    exit /b 1
)
echo SUCCESS: Frontend built

REM Port configuration
echo [3/8] Configuring ports...
if not exist ".env" (
    echo Creating default configuration...
    (
        echo WEB_PORT=18080
        echo MYSQL_PORT=13306
        echo MYSQL_ROOT_PASSWORD=ljl18420
        echo MYSQL_DATABASE=user_system
        echo MYSQL_USER=docs_user
        echo MYSQL_PASSWORD=ljl18420
        echo SECRET_KEY=your-super-secure-secret-key-for-production-change-this-immediately
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo REFRESH_TOKEN_EXPIRE_DAYS=7
        echo DATABASE_POOL_SIZE=20
        echo DATABASE_MAX_OVERFLOW=30
        echo DATABASE_POOL_RECYCLE=3600
    ) > .env
)
echo SUCCESS: Port configuration complete

REM Clean old containers
echo [4/8] Cleaning old containers...
docker-compose down >nul 2>&1
echo SUCCESS: Container cleanup complete

REM Build images
echo [5/8] Building Docker images...
echo Building images, please wait...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Image build failed
    pause
    exit /b 1
)
echo SUCCESS: Image build complete

REM Start services
echo [6/8] Starting Docker services...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Service startup failed
    pause
    exit /b 1
)
echo SUCCESS: Services started

REM Wait for services
echo [7/8] Waiting for services to be ready...
echo Waiting for MySQL database startup...
timeout /t 15 >nul

echo [8/8] Verifying deployment status...
docker-compose ps
echo.

echo SUCCESS: Deployment complete!
echo ================================
echo.
echo Application URL: http://localhost:18080
echo API Documentation: http://localhost:18080/docs
echo System Status: http://localhost:18080/lb_status
echo.
echo Test Account:
echo   Username: abc
echo   Password: ljl18420
echo   Email: ljlaa@qq.com
echo.
echo Management Commands:
echo   Check status: docker-compose ps
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo.

pause