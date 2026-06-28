#!/bin/bash

# 简单上传脚本 - 上传backend目录到NAS

NAS_IP="192.168.31.105"
NAS_USER="Kirito"
NAS_PATH="/vol2/1000/Docker/anquan"

echo "=== 上传backend目录到NAS ==="
echo "目标路径: ${NAS_USER}@${NAS_IP}:${NAS_PATH}"
echo ""

# 打包backend目录
echo "打包backend目录..."
cd /Users/kirito/Downloads/12/111
tar -czf backend.tar.gz backend/
echo "✓ 打包完成"
echo ""

# 上传到NAS
echo "上传到NAS..."
scp backend.tar.gz ${NAS_USER}@${NAS_IP}:${NAS_PATH}/
echo "✓ 上传完成"
echo ""

# 清理本地文件
rm backend.tar.gz
echo "✓ 清理本地临时文件"
echo ""

echo "=== 上传成功 ==="
echo "文件位置: ${NAS_PATH}/backend.tar.gz"
echo ""
echo "下一步：SSH到NAS并运行解压和部署命令"
echo "ssh ${NAS_USER}@${NAS_IP}"
echo "cd ${NAS_PATH}"
echo "tar -xzf backend.tar.gz"
echo "cd backend && docker-compose up -d --build"