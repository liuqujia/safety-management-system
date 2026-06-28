#!/bin/bash

# 安全整改管理系统 NAS部署脚本 - 定制版

# NAS配置参数
NAS_IP="192.168.31.105"
NAS_USER="Kirito"
NAS_DOCKER_PATH="/vol2/1000/Docker/anquan"
LOCAL_BACKEND_PATH="/Users/kirito/Downloads/12/111/backend"

echo "=== 安全整改管理系统 NAS部署脚本 ==="
echo "NAS IP: ${NAS_IP}"
echo "NAS用户: ${NAS_USER}"
echo "Docker路径: ${NAS_DOCKER_PATH}"
echo ""

# 步骤1: 打包backend目录
echo "1. 打包backend目录..."
cd "$(dirname "$LOCAL_BACKEND_PATH")"
tar -czf backend.tar.gz backend/
echo "✓ 打包完成: backend.tar.gz"
echo ""

# 步骤2: 上传到NAS
echo "2. 上传到NAS（需要输入密码）..."
scp backend.tar.gz ${NAS_USER}@${NAS_IP}:/tmp/
if [ $? -eq 0 ]; then
    echo "✓ 上传完成"
else
    echo "✗ 上传失败，请检查网络连接和密码"
    exit 1
fi
echo ""

# 步骤3: SSH到NAS并部署
echo "3. SSH到NAS并部署（需要再次输入密码）..."
ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'

echo "=== 开始在NAS上部署 ==="

# 创建项目目录
echo "创建项目目录..."
mkdir -p /vol2/1000/Docker/anquan
cd /vol2/1000/Docker/anquan

# 清理旧文件（如果存在）
if [ -d "backend" ]; then
    echo "清理旧文件..."
    rm -rf backend
fi
if [ -f "docker-compose.yml" ]; then
    echo "备份旧配置..."
    mv docker-compose.yml docker-compose.yml.bak
fi

# 解压文件
echo "解压文件..."
tar -xzf /tmp/backend.tar.gz

# 移动文件到正确位置
cd backend
echo "文件列表:"
ls -la

# 创建数据目录
echo "创建数据目录..."
mkdir -p data/photos
chmod -R 755 data

# 构建Docker镜像
echo "构建Docker镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
sleep 5

# 查看状态
echo ""
echo "=== 部署完成 ==="
echo "服务状态:"
docker-compose ps

echo ""
echo "服务日志:"
docker-compose logs --tail=20

echo ""
echo "=== 访问地址 ==="
echo "本地访问: http://localhost:9999"
echo "局域网访问: http://192.168.31.105:9999"
echo "API文档: http://192.168.31.105:9999/docs"

# 清理临时文件
rm /tmp/backend.tar.gz

ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=== ✅ 部署成功 ==="
    echo "API服务地址: http://${NAS_IP}:9999"
    echo "API文档地址: http://${NAS_IP}:9999/docs"
    echo "数据库位置: ${NAS_DOCKER_PATH}/backend/data/safety_management.db"
    echo "照片存储位置: ${NAS_DOCKER_PATH}/backend/data/photos/"
    echo ""
else
    echo ""
    echo "=== ✗ 部署失败 ==="
    echo "请检查SSH连接和Docker配置"
fi

# 清理本地打包文件
rm backend.tar.gz
echo "清理本地临时文件完成"