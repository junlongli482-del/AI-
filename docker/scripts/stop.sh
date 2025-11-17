#!/bin/bash

# 🛑 Vue3 + FastAPI 文档管理系统 - 停止脚本
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${2}${1}${NC}"
}

print_message "🛑 停止 Vue3 + FastAPI 文档管理系统" $BLUE
print_message "====================================" $BLUE
echo

# 检查是否有运行中的容器
if ! docker-compose ps -q | grep -q .; then
    print_message "⚠️  没有发现运行中的容器" $YELLOW
    exit 0
fi

# 显示当前运行的容器
print_message "📋 当前运行的容器:" $BLUE
docker-compose ps
echo

# 询问停止方式
print_message "请选择停止方式:" $YELLOW
echo "1) 正常停止 (保留数据)"
echo "2) 停止并删除容器 (保留数据卷)"
echo "3) 完全清理 (删除容器和数据卷)"
echo "4) 取消"
echo

read -p "请选择 (1-4): " choice

case $choice in
    1)
        print_message "🔄 正常停止容器..." $BLUE
        docker-compose stop
        print_message "✅ 容器已停止" $GREEN
        ;;
    2)
        print_message "🔄 停止并删除容器..." $BLUE
        docker-compose down
        print_message "✅ 容器已删除，数据卷已保留" $GREEN
        ;;
    3)
        print_message "⚠️  这将删除所有数据，包括数据库和上传的文件！" $RED
        read -p "确认删除所有数据？(输入 'YES' 确认): " confirm
        if [ "$confirm" = "YES" ]; then
            print_message "🔄 完全清理..." $BLUE
            docker-compose down --volumes --rmi local
            print_message "✅ 已完全清理" $GREEN
        else
            print_message "❌ 操作已取消" $YELLOW
        fi
        ;;
    4)
        print_message "❌ 操作已取消" $YELLOW
        exit 0
        ;;
    *)
        print_message "❌ 无效选择" $RED
        exit 1
        ;;
esac

echo
print_message "💡 重新启动命令: ./scripts/deploy.sh" $BLUE