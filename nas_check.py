#!/usr/bin/env python3
import paramiko, sys

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"
NAS_BACKEND = "/vol2/1000/Docker/anquan/backend"

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    stdin.close()
    return stdout.read().decode('utf-8', errors='replace').strip()

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=15)
    print("✅ 连接成功\n")
except Exception as e:
    print(f"❌ 连接失败: {e}")
    sys.exit(1)

print("=== 诊断结果 ===\n")

# 1. 代码里有没有 preview-from-word
print("1. NAS代码包含 preview-from-word:")
cnt = run(ssh, f"grep -c 'preview-from-word' {NAS_BACKEND}/app/api/issues.py 2>&1")
print(f"   匹配次数: {cnt}")

# 2. 容器是否运行
print("\n2. 容器状态:")
ct = run(ssh, "docker ps --filter name=anquan --format '{{.Names}} {{.Status}}'")
print(f"   {ct or '未找到容器'}")

# 3. 最后日志
print("\n3. 容器日志末尾:")
log = run(ssh, "docker logs $(docker ps -q --filter name=anquan 2>/dev/null | head -1) 2>&1 | tail -10")
print(f"   {log or '(无日志)'}")

# 4. 容器内有没有这个接口
print("\n4. 容器内Python路由:")
routes = run(ssh,
    "docker exec $(docker ps -q --filter name=anquan 2>/dev/null | head -1) "
    "python3 -c \"from app.api.issues import router; print([r.path for r in router.routes])\" 2>&1"
)
print(f"   {routes}")

# 5. 直接在容器内curl测试
print("\n5. 容器内测试接口:")
resp = run(ssh,
    "docker exec $(docker ps -q --filter name=anquan 2>/dev/null | head -1) "
    "curl -s -X POST http://localhost:8000/api/issues/preview-from-word "
    "-F 'file=@/dev/null' 2>&1 | head -c 200"
)
print(f"   {resp or '(无响应)'}")

ssh.close()
