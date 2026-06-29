#!/bin/bash

################################################################################
# 飞牛NAS (fnOS) Vue前端一键部署脚本
# 作者: Claude AI
# 版本: 1.0.0
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
NAS_IP="192.168.31.105"
NAS_USER="Kirito"
NAS_DOCKER_PATH="/vol2/1000/Docker"
NAS_PROJECT_PATH="${NAS_DOCKER_PATH}/safety-vue"
LOCAL_PROJECT_PATH="/Users/kirito/Downloads/12/111/safety-vue"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印分隔线
print_separator() {
    echo "============================================================================"
}

################################################################################
# 主流程
################################################################################

main() {
    print_separator
    print_info "飞牛NAS Vue前端一键部署脚本"
    print_separator
    echo ""

    # 步骤1: 检查本地环境
    print_info "步骤1: 检查本地环境..."
    if [ ! -d "${LOCAL_PROJECT_PATH}" ]; then
        print_error "本地项目目录不存在: ${LOCAL_PROJECT_PATH}"
        print_info "请确保您已克隆或下载项目代码"
        exit 1
    fi

    cd "${LOCAL_PROJECT_PATH}"

    # 检查npm是否安装
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装，请先安装 Node.js"
        exit 1
    fi

    print_success "本地环境检查完成"
    echo ""

    # 步骤2: 安装依赖并构建
    print_info "步骤2: 安装依赖并构建项目..."

    if [ ! -d "node_modules" ]; then
        print_info "安装npm依赖（首次需要几分钟）..."
        npm install
        if [ $? -ne 0 ]; then
            print_error "npm install 失败"
            exit 1
        fi
    fi

    print_info "构建生产版本..."
    npm run build

    if [ $? -ne 0 ]; then
        print_error "构建失败"
        exit 1
    fi

    if [ ! -d "dist" ]; then
        print_error "构建输出目录 dist 不存在"
        exit 1
    fi

    print_success "项目构建完成"
    echo ""

    # 步骤3: 检查NAS连接
    print_info "步骤3: 检查NAS连接..."
    if ! ssh -o ConnectTimeout=5 ${NAS_USER}@${NAS_IP} "echo 'Connection OK'" &> /dev/null; then
        print_error "无法连接到飞牛NAS (${NAS_IP})"
        print_info "请检查："
        print_info "  1. NAS IP地址是否正确"
        print_info "  2. SSH服务是否启动"
        print_info "  3. 网络连接是否正常"
        exit 1
    fi
    print_success "NAS连接成功"
    echo ""

    # 步骤4: 在NAS上创建目录
    print_info "步骤4: 在NAS上创建项目目录..."
    ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'
        mkdir -p /vol2/1000/Docker/safety-vue
        chmod -R 755 /vol2/1000/Docker
        echo "目录创建完成"
ENDSSH

    if [ $? -ne 0 ]; then
        print_error "创建NAS目录失败"
        exit 1
    fi
    print_success "NAS目录创建完成"
    echo ""

    # 步骤5: 上传文件到NAS
    print_info "步骤5: 上传文件到NAS..."
    print_info "这可能需要几分钟，请耐心等待..."

    # 上传dist目录
    scp -r dist ${NAS_USER}@${NAS_IP}:${NAS_PROJECT_PATH}/

    # 上传配置文件
    scp docker-compose.yml fnos-nginx.conf ${NAS_USER}@${NAS_IP}:${NAS_PROJECT_PATH}/

    if [ $? -ne 0 ]; then
        print_error "文件上传失败"
        exit 1
    fi
    print_success "文件上传完成"
    echo ""

    # 步骤6: 在NAS上启动服务
    print_info "步骤6: 在NAS上启动Docker服务..."

    ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'
        cd /vol2/1000/Docker/safety-vue

        echo "停止旧容器（如果存在）..."
        docker compose down 2>/dev/null || true

        echo "启动新容器..."
        docker compose up -d

        echo ""
        echo "检查容器状态..."
        sleep 3
        docker ps | grep vue-frontend

        echo ""
        echo "查看容器日志..."
        docker logs vue-frontend 2>&1 | tail -20
ENDSSH

    if [ $? -ne 0 ]; then
        print_error "Docker服务启动失败"
        print_info "请手动检查NAS上的Docker状态"
        exit 1
    fi
    print_success "Docker服务启动完成"
    echo ""

    # 完成
    print_separator
    print_success "部署完成！"
    print_separator
    echo ""
    echo "🎉 恭喜！Vue前端已成功部署到飞牛NAS"
    echo ""
    echo "📱 访问地址："
    echo "   - Vue前端: http://${NAS_IP}:8866/"
    echo "   - 后端API: http://${NAS_IP}:9999"
    echo "   - API文档: http://${NAS_IP}:9999/docs"
    echo ""
    echo "📝 NAS项目目录: ${NAS_PROJECT_PATH}"
    echo ""
    echo "🔧 常用命令："
    echo "   - 查看日志: docker logs -f vue-frontend"
    echo "   - 重启服务: docker compose restart"
    echo "   - 停止服务: docker compose down"
    echo ""
    print_separator
}

# 运行主函数
main "$@"