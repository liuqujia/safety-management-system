#!/usr/bin/env python3
"""NAS 诊断 v2 - 解决 sudo docker 权限问题"""
import paramiko, sys

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"
NAS_BACKEND = "/vol2/1000/Docker/anquan/backend"
PW = NAS_PASSWORD

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdin.write(PW + "\n")
    stdin.flush()
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

# 1. 代码有没有新接口
print("1. NAS代码包含 preview-from-word:")
cnt = run(ssh, f"echo {PW} | sudo -S grep -c 'preview-from-word' {NAS_BACKEND}/app/api/issues.py 2>&1")
print(f"   匹配次数: {cnt}")

# 2. 查看所有容器
print("\n2. 所有 Docker 容器:")
ct = run(ssh, f"echo {PW} | sudo -S docker ps -a --format '{{.Names}} {{.Status}}'")
print(f"   {ct or '(无容器)'}")

# 3. 查看 compose 文件
print("\n3. docker-compose.yml 内容:")
yml = run(ssh, f"echo {PW} | sudo -S cat {NAS_BACKEND}/docker-compose.yml")
print(f"   {yml[:300]}")

# 4. 启动容器
print("\n4. 尝试启动容器...")
out = run(ssh, f"cd {NAS_BACKEND} && echo {PW} | sudo -S docker compose up -d 2>&1", timeout=180)
print(f"   {out[-400:]}")

# 5. 等待启动
import time
print("\n5. 等待容器启动（15秒）...")
time.sleep(15)

print("\n6. 容器状态:")
ct2 = run(ssh, f"echo {PW} | sudo -S docker ps --format '{{.Names}} {{.Status}}'")
print(f"   {ct2 or '(无运行中容器)'}")

# 6. 日志
container = run(ssh, f"echo {PW} | sudo -S docker ps -q | head -1")
if container:
    print(f"\n7. 容器日志:")
    log = run(ssh, f"echo {PW} | sudo -S docker logs {container} 2>&1 | tail -15")
    print(f"   {log}")
else:
    print("\n7. 容器仍未运行，查看 docker-compose up 输出:")
    out2 = run(ssh, f"cd {NAS_BACKEND} && echo {PW} | sudo -S docker compose up 2>&1 | tail -20", timeout=60)
    print(f"   {out2}")

ssh.close()
