#!/bin/bash

echo "=== 飞牛NAS Vue前端一键部署脚本（简化版）==="
echo ""

NAS_IP="192.168.31.105"
NAS_USER="Kirito"
NAS_PATH="/vol2/1000/Docker/safety-vue-simple"
LOCAL_PATH="/Users/kirito/Downloads/12/111/safety-vue-simple"

# 1. 上传到NAS
echo "1. 上传文件到NAS..."
scp -r ${LOCAL_PATH} ${NAS_USER}@${NAS_IP}:/vol2/1000/Docker/

# 2. SSH到NAS执行
echo "2. 在NAS上构建并启动..."
ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'
cd /vol2/1000/Docker/safety-vue-simple

# 安装npm依赖
echo "安装npm依赖..."
npm config set registry https://registry.npmmirror.com
npm install --legacy-peer-deps

# 构建
echo "构建项目..."
npm run build

# 停止旧容器
echo "停止旧容器..."
docker compose down 2>/dev/null || true

# 启动新容器
echo "启动Docker容器..."
docker compose up -d

echo ""
echo "部署完成！"
echo "访问地址: http://192.168.31.105:8866/"
ENDSSH

echo ""
echo "=== 完成 ==="