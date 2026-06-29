#!/usr/bin/env python3
"""飞牛(FNOS) NAS 重建后端容器"""
import paramiko, sys, time

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"
NAS_BACKEND = "/vol2/1000/Docker/anquan/backend"
PW = NAS_PASSWORD

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=False)
    stdin.write(PW + "\n")
    stdin.flush()
    stdin.close()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def run_quiet(ssh, cmd, timeout=30):
    """不带密码交互的简单命令"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
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

# 1. 检查代码
print("1. 检查NAS代码...")
cnt = run_quiet(ssh, f"grep -c 'preview-from-word' {NAS_BACKEND}/app/api/issues.py 2>&1 || echo 0")
print(f"   preview-from-word 出现次数: {cnt}")

# 2. 检查 docker compose 文件
print("\n2. 检查 docker-compose.yml...")
yml = run_quiet(ssh, f"cat {NAS_BACKEND}/docker-compose.yml 2>&1")
print(f"   {yml[:200]}")

# 3. 重建容器
print("\n3. 重建后端容器（需要约1-2分钟）...")
print("   先停止现有容器...")
run(ssh, f"cd {NAS_BACKEND} && echo {PW} | sudo -S docker compose down 2>&1", timeout=30)
time.sleep(2)

print("   重新构建并启动...")
out, err = run(ssh, f"cd {NAS_BACKEND} && echo {PW} | sudo -S docker compose up -d --build 2>&1", timeout=300)
print(f"   输出: {out[-500:]}")
if err.strip():
    print(f"   ⚠ 错误: {err[-300:]}")

# 4. 等待容器就绪
print("\n4. 等待容器启动（45秒）...")
time.sleep(45)

# 5. 检查状态
print("\n5. 容器状态:")
ct = run_quiet(ssh, f"echo {PW} | sudo -S docker ps --format '{{{{.Names}}}} {{{{.Status}}}}' 2>&1")
print(f"   {ct}")

# 6. 容器日志
container_name = run_quiet(ssh, f"echo {PW} | sudo -S docker ps -q --filter name=safety 2>&1 | head -1")
if container_name:
    print(f"\n6. 容器日志末尾:")
    log = run_quiet(ssh, f"echo {PW} | sudo -S docker logs {container_name} 2>&1 | tail -15")
    print(f"   {log}")

# 7. 测试接口
print("\n7. 测试 preview-from-word 接口:")
resp = run_quiet(ssh, f"curl -s -X POST http://localhost:9999/api/issues/preview-from-word -F 'file=@/dev/null' 2>&1 | head -c 300")
if "405" in resp or not resp:
    print(f"   ⚠ 响应: {resp[:100] or '(无响应)'}")
else:
    print(f"   ✅ {resp[:150]}")

ssh.close()
print("\n🎉 完成!")
