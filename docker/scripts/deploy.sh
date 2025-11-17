#!/bin/bash

# 🚀 Vue3 + FastAPI 文档管理系统 - Docker一键部署脚本
# ========================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo
    print_message "🐳 Vue3 + FastAPI 文档管理系统 - Docker部署" $CYAN
    print_message "================================================" $CYAN
    echo
}

print_step() {
    print_message "[$1] $2" $BLUE
}

print_success() {
    print_message "✅ $1" $GREEN
}

print_warning() {
    print_message "⚠️  $1" $YELLOW
}

print_error() {
    print_message "❌ $1" $RED
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2

    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            print_warning "$service 端口 $port 已被占用"
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            print_warning "$service 端口 $port 已被占用"
            return 1
        fi
    else
        print_warning "无法检测端口占用情况（缺少 netstat 或 ss 命令）"
        return 0
    fi

    print_success "$service 端口 $port 可用"
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

# 主函数
main() {
    print_header

    # 1. 检查Docker环境
    print_step "1/8" "检查Docker环境..."
    check_command "docker"
    check_command "docker-compose"
    print_success "Docker环境检查通过"

    # 2. 检查前端构建
    print_step "2/8" "检查前端构建..."
    if [ ! -f "../vue3/dist/index.html" ]; then
        print_warning "前端未构建，正在构建..."
        cd ../vue3
        if command -v npm &> /dev/null; then
            npm run build
            print_success "前端构建完成"
        else
            print_error "npm未安装，请先构建前端: cd vue3 && npm run build"
            exit 1
        fi
        cd ../docker
    else
        print_success "前端已构建"
    fi

    # 3. 端口配置
    print_step "3/8" "配置端口..."

    # 读取现有配置或使用默认值
    if [ -f ".env" ]; then
        source .env
    fi

    WEB_PORT=${WEB_PORT:-18080}
    MYSQL_PORT=${MYSQL_PORT:-13306}

    # 检查端口占用
    web_port_ok=true
    mysql_port_ok=true

    if ! check_port $WEB_PORT "Web服务"; then
        web_port_ok=false
        suggested_web_port=$(suggest_port 18080)
        print_message "💡 建议使用端口: $suggested_web_port" $YELLOW
    fi

    if ! check_port $MYSQL_PORT "MySQL服务"; then
        mysql_port_ok=false
        suggested_mysql_port=$(suggest_port 13306)
        print_message "💡 建议使用端口: $suggested_mysql_port" $YELLOW
    fi

    # 如果有端口冲突，询问用户
    if [ "$web_port_ok" = false ] || [ "$mysql_port_ok" = false ]; then
        echo
        print_message "检测到端口冲突，请选择处理方式：" $YELLOW
        echo "1) 自动使用建议端口"
        echo "2) 手动输入端口"
        echo "3) 退出，手动修改 .env 文件"
        echo
        read -p "请选择 (1-3): " choice

        case $choice in
            1)
                if [ "$web_port_ok" = false ]; then
                    WEB_PORT=$suggested_web_port
                fi
                if [ "$mysql_port_ok" = false ]; then
                    MYSQL_PORT=$suggested_mysql_port
                fi
                ;;
            2)
                if [ "$web_port_ok" = false ]; then
                    read -p "请输入Web访问端口 (建议 $suggested_web_port): " input_web_port
                    WEB_PORT=${input_web_port:-$suggested_web_port}
                fi
                if [ "$mysql_port_ok" = false ]; then
                    read -p "请输入MySQL端口 (建议 $suggested_mysql_port): " input_mysql_port
                    MYSQL_PORT=${input_mysql_port:-$suggested_mysql_port}
                fi
                ;;
            3)
                print_message "请手动修改 .env 文件中的端口配置，然后重新运行此脚本" $YELLOW
                exit 0
                ;;
            *)
                print_error "无效选择"
                exit 1
                ;;
        esac
    fi

    # 更新 .env 文件
    cat > .env << EOF
# 🎯 Vue3 + FastAPI 文档管理系统 - Docker配置
# ================================================

# 🌐 Web访问端口配置
WEB_PORT=$WEB_PORT

# 🗄️ MySQL数据库配置
MYSQL_PORT=$MYSQL_PORT
MYSQL_ROOT_PASSWORD=ljl18420
MYSQL_DATABASE=user_system
MYSQL_USER=docs_user
MYSQL_PASSWORD=ljl18420

# 🔐 应用安全配置
SECRET_KEY=your-super-secure-secret-key-for-production-change-this-immediately
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 🚀 性能配置
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_RECYCLE=3600
EOF

    print_success "端口配置完成: Web=$WEB_PORT, MySQL=$MYSQL_PORT"

    # 4. 清理旧容器
    print_step "4/8" "清理旧容器..."
    if docker-compose ps -q | grep -q .; then
        print_message "发现运行中的容器，正在停止..." $YELLOW
        docker-compose down
    fi
    print_success "容器清理完成"

    # 5. 构建镜像
    print_step "5/8" "构建Docker镜像..."
    docker-compose build --no-cache
    print_success "镜像构建完成"

    # 6. 启动服务
    print_step "6/8" "启动Docker服务..."
    docker-compose up -d
    print_success "服务启动完成"

    # 7. 等待服务就绪
    print_step "7/8" "等待服务就绪..."
    echo "正在等待MySQL数据库启动..."

    # 等待MySQL就绪
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T mysql mysqladmin ping -h localhost -u root -pljl18420 --silent; then
            break
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    echo

    if [ $attempt -eq $max_attempts ]; then
        print_error "MySQL启动超时"
        exit 1
    fi

    print_success "MySQL数据库就绪"

    # 等待FastAPI就绪
    echo "正在等待FastAPI服务启动..."
    max_attempts=20
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$WEB_PORT/api/health >/dev/null 2>&1; then
            break
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    echo

    if [ $attempt -eq $max_attempts ]; then
        print_warning "FastAPI服务启动可能需要更多时间"
    else
        print_success "FastAPI服务就绪"
    fi

    # 8. 验证部署
    print_step "8/8" "验证部署状态..."

    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        print_success "所有容器运行正常"
    else
        print_error "部分容器启动失败"
        docker-compose ps
        exit 1
    fi

    # 部署完成
    echo
    print_message "🎉 部署完成！" $GREEN
    print_message "================================" $GREEN
    echo
    print_message "📱 应用访问地址:" $CYAN
    print_message "   http://localhost:$WEB_PORT" $GREEN
    echo
    print_message "📚 API文档地址:" $CYAN
    print_message "   http://localhost:$WEB_PORT/docs" $GREEN
    echo
    print_message "📊 系统状态:" $CYAN
    print_message "   http://localhost:$WEB_PORT/lb_status" $GREEN
    echo
    print_message "🗄️ 数据库连接:" $CYAN
    print_message "   Host: localhost:$MYSQL_PORT" $GREEN
    print_message "   Database: user_system" $GREEN
    print_message "   Username: docs_user" $GREEN
    print_message "   Password: ljl18420" $GREEN
    echo
    print_message "🧪 测试账号:" $CYAN
    print_message "   用户名: abc" $GREEN
    print_message "   密码: ljl18420" $GREEN
    print_message "   邮箱: ljlaa@qq.com" $GREEN
    echo
    print_message "🔧 管理命令:" $CYAN
    print_message "   查看状态: docker-compose ps" $YELLOW
    print_message "   查看日志: docker-compose logs -f" $YELLOW
    print_message "   重启服务: docker-compose restart" $YELLOW
    print_message "   停止服务: docker-compose down" $YELLOW
    echo
    print_message "💡 如需修改端口，请编辑 .env 文件后重新启动" $BLUE
    echo
}

# 执行主函数
main "$@"