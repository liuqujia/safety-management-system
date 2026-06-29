#!/usr/bin/env python3
"""NAS 诊断脚本 - 查清楚为什么还是 405"""
import paramiko
import sys

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"
NAS_BACKEND = "/vol2/1000/Docker/anquan/backend"

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    stdin.close()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=15)
    print("✅ 连接成功\n")
except Exception as e:
    print(f"❌ 连接失败: {e}")
    sys.exit(1)

# 1. 检查 issues.py 里有没有 preview-from-word
print("1. 检查 issues.py 源码是否包含 preview-from-word:")
out, _ = run(ssh, f"grep -c 'preview-from-word' {NAS_BACKEND}/app/api/issues.py 2>&1 || echo 'FILE NOT FOUND'")
print(f"   匹配次数: {out}")

# 2. 看构建日志
print("\n2. 最后20行 Docker 构建日志:")
out, err = run(ssh, f"docker logs $(docker ps -q --filter name=anquan 2>/dev/null | head -1) 2>&1 | tail -20")
print(f"   {out or '(无日志)'}")
print(f"   ⚠ {err[:200]}" if err else "")

# 3. 直接在容器里测试接口
print("\n3. 容器内直接测试接口:")
out, _ = run(ssh,
    "docker exec $(docker ps -q --filter name=anquan | head -1) "
    "curl -s -X POST http://localhost:8000/api/issues/preview-from-word "
    "-F 'file=@/dev/null' 2>&1 | head -c 300"
)
print(f"   响应: {out or '(无响应)'}")

# 4. 看路由注册情况
print("\n4. 容器内 Python 路由列表:")
out, _ = run(ssh,
    "docker exec $(docker ps -q --filter name=anquan | head -1) "
    "python3 -c \"from app.api.issues import router; print([r.path for r in router.routes])\" 2>&1"
)
print(f"   {out}")

# 5. Docker 镜像构建时间
print("\n5. 容器镜像信息:")
out, _ = run(ssh,
    "docker inspect $(docker ps -q --filter name=anquan | head -1) "
    "--format '{{.Config.Image}} | Built: {{.Created}}'"
)
print(f"   {out}")

ssh.close()
