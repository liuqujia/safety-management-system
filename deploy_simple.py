#!/usr/bin/env python3
"""简化版NAS部署脚本 - 跳过本地构建，直接上传预构建的dist"""
import paramiko
import os
import sys
import time

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"
NAS_BACKEND_PATH = "/vol2/1000/Docker/anquan/backend"
BASE = "/Users/kirito/Downloads/12/111"

def remote_exec(ssh_client, cmd_str, timeout=120):
    print(f"  → {cmd_str[:70]}...")
    stdin, stdout, stderr = ssh_client.exec_command(cmd_str, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if err.strip():
        print(f"    ⚠ {err.strip()[:150]}")
    return out, err

def upload_dir(sftp, local_dir, remote_dir):
    remote_exec(ssh, f"mkdir -p {remote_dir}")
    for item in os.listdir(local_dir):
        local_item = os.path.join(local_dir, item)
        remote_item = f"{remote_dir}/{item}"
        if os.path.isfile(local_item):
            try: sftp.stat(remote_item); sftp.remove(remote_item)
            except: pass
            sftp.put(local_item, remote_item)
        elif os.path.isdir(local_item):
            upload_dir(sftp, local_item, remote_item)

# ── 连接 ──
print("🔌 连接NAS...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=10)
    print(" ✅ 连接成功")
except Exception as e:
    print(f" ❌ 连接失败: {e}")
    sys.exit(1)

sftp = ssh.open_sftp()

# ── 1/3 上传 backend ──
print("\n1/3 在NAS上创建目录...")
remote_exec(ssh, f"mkdir -p {NAS_BACKEND_PATH}")
remote_exec(ssh, "mkdir -p /vol1/1000/工作资料/安全资料/photos")

print("\n2/3 上传 backend 代码...")
remote_exec(ssh, f"rm -rf {NAS_BACKEND_PATH}/*")
local_backend = os.path.join(BASE, "backend")
upload_dir(sftp, local_backend, NAS_BACKEND_PATH)
print(" ✅ 上传完成")

# ── 3/3 上传前端dist + nginx配置 ──
print("\n3/3 上传前端 dist + 重启服务...")
DIST = os.path.join(BASE, "safety-vue", "dist")
NAS_FE = "/vol2/1000/Docker/anquan/safety-vue"

if not os.path.isdir(DIST):
    print(f" ❌ dist 目录不存在: {DIST}")
    print(f"   请在项目目录下运行: cd safety-vue && pnpm install && pnpm build")
    sys.exit(1)

dist_kb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DIST) for f in fs) // 1024
print(f" 📦 预构建 dist ({dist_kb} KB)，上传到 NAS...")

# 上传 dist/
remote_exec(ssh, f"mkdir -p {NAS_FE}/dist")
remote_exec(ssh, f"rm -rf {NAS_FE}/dist/*")
for item in os.listdir(DIST):
    local_item = os.path.join(DIST, item)
    remote_item = f"{NAS_FE}/dist/{item}"
    if os.path.isfile(local_item):
        try: sftp.stat(remote_item); sftp.remove(remote_item)
        except: pass
        sftp.put(local_item, remote_item)
    elif os.path.isdir(local_item):
        upload_dir(sftp, local_item, remote_item)
print(" ✅ dist 上传完成")

# 上传 nginx/docker 配置
for fname in ["docker-compose.yml", "fnos-nginx.conf"]:
    local_f = os.path.join(BASE, "safety-vue", fname)
    if os.path.isfile(local_f):
        sftp.put(local_f, f"{NAS_FE}/{fname}")
        print(f" ✅ {fname} 已上传")

# 重启后端 Docker
print("\n🔄 重启后端 Docker...")
remote_exec(ssh,
    f"cd {NAS_BACKEND_PATH} && docker compose down 2>/dev/null && docker compose up -d",
    timeout=180
)
print(" ✅ 后端已重启")

# 重启前端 Docker
print("🔄 重启前端 Docker...")
remote_exec(ssh,
    f"cd {NAS_FE} && docker compose down 2>/dev/null && docker compose up -d",
    timeout=120
)
print(" ✅ 前端已重启")

sftp.close()
ssh.close()
print("\n🎉 全部完成!")
print("   前端: http://192.168.31.105:8866")
print("   后端: http://192.168.31.105:9999")
print("   API文档: http://192.168.31.105:9999/docs")
