#!/bin/bash

# NAS部署指南 - 在NAS上运行的命令

echo "=== 在NAS上执行以下命令 ==="
echo ""

echo "# 1. SSH登录NAS"
echo "ssh Kirito@192.168.31.105"
echo ""

echo "# 2. 进入项目目录"
echo "cd /vol2/1000/Docker/anquan"
echo ""

echo "# 3. 解压文件（如果已上传backend.tar.gz）"
echo "tar -xzf backend.tar.gz"
echo ""

echo "# 4. 进入backend目录"
echo "cd backend"
echo ""

echo "# 5. 创建数据目录"
echo "mkdir -p /vol1/1000/工作资料/安全资料/photos"
echo "chmod -R 755 /vol1/1000/工作资料/安全资料"
echo ""

echo "# 6. 构建并启动Docker服务"
echo "docker-compose up -d --build"
echo ""

echo "# 7. 查看服务状态"
echo "docker-compose ps"
echo ""

echo "# 8. 查看日志"
echo "docker-compose logs -f"
echo ""

echo "# 9. 测试API"
echo "curl http://localhost:9999"
echo ""

echo "=== 访问地址 ==="
echo "API服务: http://192.168.31.105:9999"
echo "API文档: http://192.168.31.105:9999/docs"
echo ""

echo "=== 数据存储位置 ==="
echo "数据库: /vol1/1000/工作资料/安全资料/safety_management.db"
echo "照片: /vol1/1000/工作资料/安全资料/photos/"
echo ""