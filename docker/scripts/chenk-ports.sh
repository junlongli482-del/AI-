#!/bin/bash

# 🔍 端口检测脚本
# ===============

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${2}${1}${NC}"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2

    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            print_message "❌ $service 端口 $port 已被占用" $RED
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            print_message "❌ $service 端口 $port 已被占用" $RED
            return 1
        fi
    else
        print_message "⚠️  无法检测端口占用情况（缺少 netstat 或 ss 命令）" $YELLOW
        return 0
    fi

    print_message "✅ $service 端口 $port 可用" $GREEN
    return 0
}

# 建议可用端口
suggest_port() {
    local base_port=$1
    local port=$base_port

    while ! check_port $port "临时检测" >/dev/null 2>&1; do
        port=$((port + 1))
    done

    echo $port
}

print_message "🔍 端口占用检测" $BLUE
print_message "===============" $BLUE
echo

# 读取配置
if [ -f ".env" ]; then
    source .env
fi

WEB_PORT=${WEB_PORT:-18080}
MYSQL_PORT=${MYSQL_PORT:-13306}

print_message "当前配置的端口:" $BLUE
echo "Web端口: $WEB_PORT"
echo "MySQL端口: $MYSQL_PORT"
echo

print_message "检测结果:" $BLUE

# 检查Web端口
check_port $WEB_PORT "Web服务"
web_ok=$?

# 检查MySQL端口
check_port $MYSQL_PORT "MySQL服务"
mysql_ok=$?

echo

if [ $web_ok -eq 0 ] && [ $mysql_ok -eq 0 ]; then
    print_message "🎉 所有端口都可用，可以正常部署！" $GREEN
else
    print_message "⚠️  发现端口冲突，建议使用以下端口:" $YELLOW

    if [ $web_ok -ne 0 ]; then
        suggested_web=$(suggest_port 18080)
        echo "Web端口建议: $suggested_web"
    fi

    if [ $mysql_ok -ne 0 ]; then
        suggested_mysql=$(suggest_port 13306)
        echo "MySQL端口建议: $suggested_mysql"
    fi

    echo
    print_message "修改方法:" $BLUE
    echo "1. 编辑 .env 文件"
    echo "2. 修改对应的端口配置"
    echo "3. 重新运行 ./scripts/deploy.sh"
fi

echo
print_message "💡 常用端口范围建议:" $BLUE
echo "Web端口: 18080-18099, 28080-28099, 38080-38099"
echo "MySQL端口: 13306-13399, 23306-23399, 33306-33399"