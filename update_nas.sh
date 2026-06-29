#!/bin/bash
# NAS 一键更新脚本（运行于 /vol2/1000/Docker/anquan 目录）
# 用途：从 GitHub 拉取最新代码，重建并重启后端容器

set -e
APP_DIR="/vol2/1000/Docker/anquan"
DATA_DIR="/vol1/1000/工作资料/安全资料"
BACKEND_DIR="$APP_DIR/backend"

echo "=========================================="
echo "  安全管理系统 - 一键更新脚本"
echo "=========================================="

cd "$APP_DIR"

# 1. 检查目录
echo "[1/6] 检查目录..."
if [ ! -d "$APP_DIR/backend" ]; then
    echo "❌ 未找到 backend 目录，请确认运行在正确目录"
    exit 1
fi
echo "✅ 目录正确"

# 2. Git 配置（如果还没有）
echo "[2/6] 配置 Git 仓库..."
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/liuqujia/safety-management-system.git
    echo "✅ Git 仓库已初始化"
else
    echo "✅ Git 仓库已存在"
fi

# 3. 拉取最新代码
echo "[3/6] 拉取 GitHub 最新代码..."
git fetch origin main
git reset --hard origin/main
echo "✅ 代码已更新到最新版本"

# 4. 确认关键文件是最新的
echo "[4/6] 确认关键文件..."
if grep -q "center_alignment" "$BACKEND_DIR/app/api/export.py" 2>/dev/null; then
    echo "⚠️  警告：export.py 仍包含旧代码 center_alignment，请确认 --build 是否真正执行了"
else
    echo "✅ export.py 已包含最新修复代码"
fi

# 5. 重建 Docker 镜像并启动容器
echo "[5/6] 重建并启动容器..."
docker compose down
docker compose up -d --build
echo "✅ 容器已重建并启动"

# 6. 验证
echo "[6/6] 验证服务状态..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9999/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 后端服务运行正常 (HTTP $HTTP_CODE)"
    echo ""
    echo "🎉 更新完成！访问地址: http://192.168.31.105:9999"
else
    echo "⚠️  服务可能未正常启动，请运行 'docker compose logs' 查看日志"
fi

echo ""
echo "=========================================="
