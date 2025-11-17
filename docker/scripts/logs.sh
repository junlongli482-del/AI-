#!/bin/bash

# 📋 Vue3 + FastAPI 文档管理系统 - 日志查看脚本
# ===============================================

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_message() {
    echo -e "${2}${1}${NC}"
}

print_message "📋 Vue3 + FastAPI 文档管理系统 - 日志查看" $BLUE
print_message "========================================" $BLUE
echo

# 检查容器状态
if ! docker-compose ps -q | grep -q .; then
    print_message "⚠️  没有发现运行中的容器" $YELLOW
    exit 0
fi

# 显示菜单
print_message "请选择要查看的日志:" $BLUE
echo "1) 所有服务日志"
echo "2) Nginx 日志"
echo "3) FastAPI 日志"
echo "4) MySQL 日志"
echo "5) 实时日志 (所有服务)"
echo "6) 容器状态"
echo

read -p "请选择 (1-6): " choice

case $choice in
    1)
        print_message "📋 所有服务日志:" $GREEN
        docker-compose logs
        ;;
    2)
        print_message "📋 Nginx 日志:" $GREEN
        docker-compose logs nginx
        ;;
    3)
        print_message "📋 FastAPI 日志:" $GREEN
        docker-compose logs fastapi-1 fastapi-2 fastapi-3 fastapi-4
        ;;
    4)
        print_message "📋 MySQL 日志:" $GREEN
        docker-compose logs mysql
        ;;
    5)
        print_message "📋 实时日志 (Ctrl+C 退出):" $GREEN
        docker-compose logs -f
        ;;
    6)
        print_message "📊 容器状态:" $GREEN
        docker-compose ps
        echo
        print_message "💾 数据卷状态:" $GREEN
        docker volume ls | grep docs_
        echo
        print_message "🌐 网络状态:" $GREEN
        docker network ls | grep docs_
        ;;
    *)
        print_message "❌ 无效选择" $YELLOW
        exit 1
        ;;
esac