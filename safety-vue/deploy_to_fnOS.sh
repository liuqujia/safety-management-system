#!/bin/bash

# 飞牛NAS (fnOS) Vue前端部署脚本

echo "=== 飞牛NAS Vue前端部署脚本 ==="
echo ""

NAS_IP="192.168.31.105"
NAS_USER="Kirito"
NAS_DOCKER_PATH="/vol2/1000/Docker"
NAS_WEB_PATH="/vol1/工作资料/vue-frontend"

echo "NAS IP: ${NAS_IP}"
echo "Docker路径: ${NAS_DOCKER_PATH}"
echo "Web路径: ${NAS_WEB_PATH}"
echo ""

# 步骤1: 在Mac上构建Vue项目
echo "1. 安装依赖并构建Vue项目..."
cd "$(dirname "$0")/safety-vue"

if [ ! -d "node_modules" ]; then
    echo "安装npm依赖..."
    npm install
fi

echo "构建生产版本..."
npm run build

if [ ! -d "dist" ]; then
    echo "构建失败！"
    exit 1
fi

echo "✓ 构建完成"
echo ""

# 步骤2: 创建部署目录
echo "2. 在NAS上创建部署目录..."
ssh ${NAS_USER}@${NAS_IP} "mkdir -p ${NAS_WEB_PATH} && chmod -R 755 ${NAS_WEB_PATH}"
echo "✓ 目录创建完成"
echo ""

# 步骤3: 上传文件到NAS
echo "3. 上传Vue前端文件到NAS..."
scp -r dist/* ${NAS_USER}@${NAS_IP}:${NAS_WEB_PATH}/
echo "✓ 上传完成"
echo ""

# 步骤4: 创建反向代理配置（如果需要）
echo "4. 配置反向代理（可选）..."
echo "如果需要通过域名访问，请使用飞牛NAS的反向代理功能"
echo ""

echo "=== 部署完成 ==="
echo ""
echo "访问地址:"
echo "- Vue前端: http://${NAS_IP}:80/"
echo "- 或根据您的飞牛NAS配置访问"
echo ""
echo "API服务（后端）:"
echo "- http://${NAS_IP}:9999"
echo "- API文档: http://${NAS_IP}:9999/docs"
echo ""

# 步骤5: 配置反向代理（推荐）
echo "=== 配置反向代理（推荐）==="
echo ""
echo "在飞牛NAS管理界面中："
echo "1. 打开 '反向代理' 或 'Nginx配置'"
echo "2. 添加新的反向代理规则："
echo "   - 路径: /api"
echo "   - 目标: http://localhost:9999"
echo ""
echo "3. 保存并重启Nginx服务"
echo ""

echo "部署完成！"