#!/bin/bash

# 安全整改管理系统 NAS部署脚本

# 配置参数
NAS_IP="192.168.1.100"          # 修改为您的NAS IP地址
NAS_USER="admin"                # 修改为您的NAS用户名
NAS_PROJECT_DIR="/volume1/docker/safety-management/backend"
NAS_DATA_DIR="/vol1/1000/工作资料/安全资料"
LOCAL_DIR="/Users/kirito/Downloads/12/111/backend"

echo "=== 安全整改管理系统 NAS部署脚本 ==="
echo ""

# 步骤1: 打包backend目录
echo "1. 打包backend目录..."
cd "$(dirname "$LOCAL_DIR")"
tar -czf backend.tar.gz backend/
echo "打包完成: backend.tar.gz"
echo ""

# 步骤2: 上传到NAS
echo "2. 上传到NAS..."
echo "请输入NAS密码:"
scp backend.tar.gz ${NAS_USER}@${NAS_IP}:/tmp/
echo "上传完成"
echo ""

# 步骤3: SSH到NAS并部署
echo "3. SSH到NAS并部署..."
echo "请再次输入NAS密码:"
ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'

# 创建项目目录
echo "创建项目目录..."
mkdir -p /volume1/docker/safety-management
cd /volume1/docker/safety-management

# 解压文件
echo "解压文件..."
tar -xzf /tmp/backend.tar.gz
mv backend/* .
rm -rf backend
rm /tmp/backend.tar.gz

# 创建数据目录
echo "创建数据目录..."
mkdir -p /vol1/1000/工作资料/安全资料/photos
chmod -R 755 /vol1/1000/工作资料/安全资料

# 构建Docker镜像
echo "构建Docker镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 查看状态
echo ""
echo "=== 部署完成 ==="
echo "服务状态:"
docker-compose ps

echo ""
echo "服务日志（最后10行）:"
docker-compose logs --tail=10

echo ""
echo "API访问地址:"
echo "http://localhost:9999"
echo "http://${NAS_IP}:9999"

ENDSSH

echo ""
echo "=== 部署完成 ==="
echo "API服务地址: http://${NAS_IP}:9999"
echo "API文档地址: http://${NAS_IP}:9999/docs"
echo ""

# 清理本地打包文件
rm backend.tar.gz
echo "清理完成"