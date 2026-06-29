#!/usr/bin/env python3
"""简化版NAS部署脚本 - paramiko 无 PTY 版本"""
import paramiko
import os
import sys
import time
import tarfile
import io

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"
NAS_BACKEND_PATH = "/vol2/1000/Docker/anquan/backend"
BASE = "/Users/kirito/Downloads/12/111"

def remote_exec(ssh_client, cmd_str, timeout=120):
    """执行远程命令，无 PTY"""
    print(f"  → {cmd_str[:70]}...")
    stdin, stdout, stderr = ssh_client.exec_command(cmd_str, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if err.strip():
        print(f"    ⚠ {err.strip()[:150]}")
    return out, err

def upload_file(sftp, local_path, remote_path):
    """上传单个文件"""
    print(f"  ↑ {os.path.basename(local_path)} → {remote_path}")
    sftp.put(local_path, remote_path)

def upload_dir(sftp, local_dir, remote_base):
    """递归上传目录"""
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir)
        remote_dir = os.path.join(remote_base, rel) if rel != '.' else remote_base
        try:
            sftp.stat(remote_dir)
        except:
            sftp.mkdir(remote_dir)
        for f in files:
            local_fp = os.path.join(root, f)
            remote_fp = os.path.join(remote_dir, f)
            sftp.put(local_fp, remote_fp)

# ── 连接 ─────────────────────────────────────────────────────────────────────
print("🔌 连接NAS...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=15)
    sftp = ssh.open_sftp()
    print("  ✅ 连接成功\n")
except Exception as e:
    print(f"  ❌ 连接失败: {e}")
    sys.exit(1)

# ── 1. 创建目录 ───────────────────────────────────────────────────────────────
print("1/4 在NAS上创建目录...")
remote_exec(ssh, f"mkdir -p {NAS_BACKEND_PATH}")
remote_exec(ssh, "mkdir -p /vol1/1000/工作资料/安全资料/photos")
print("")

# ── 2. 上传 backend 代码 ─────────────────────────────────────────────────────
print("2/4 上传 backend 代码...")
t0 = time.time()
upload_dir(sftp, f"{BASE}/backend", NAS_BACKEND_PATH)
print(f"  ✅ 上传完成 ({(time.time()-t0):.0f}秒)\n")

# ── 3. 重启 Docker ───────────────────────────────────────────────────────────
print("3/4 重启后端 Docker（构建中，请等待1-2分钟）...")
out, err = remote_exec(ssh,
    f"cd {NAS_BACKEND_PATH} && docker compose down 2>/dev/null; docker compose up -d --build",
    timeout=300
)
print("  Docker输出:", out.strip()[-300:] if out.strip() else "(无输出)")
print("")

# ── 4. 等待启动 ───────────────────────────────────────────────────────────────
print("4/4 等待后端启动（30秒）...")
time.sleep(30)

# 检查状态
out, _ = remote_exec(ssh, "docker ps --filter name=anquan --format '{{.Status}}'")
print(f"  容器状态: {out.strip() or '未找到容器'}")

# 测试接口
out, _ = remote_exec(ssh,
    "curl -s -X POST http://localhost:9999/api/issues/preview-from-word "
    "-F 'file=@/dev/null' 2>&1 | head -c 200",
    timeout=20
)
resp = out.strip()
if "405" in resp or "not found" in resp.lower():
    print(f"  ❌ 接口仍返回 405，说明代码未更新")
elif resp:
    print(f"  ✅ 接口响应: {resp[:150]}")
else:
    # 尝试本地
    out2, _ = remote_exec(ssh, "curl -s http://localhost:9999/ 2>&1", timeout=10)
    print(f"  API根: {out2.strip()[:100]}")
print("")

sftp.close()
ssh.close()

print("🎉 部署完成!")
print("后端: http://192.168.31.105:9999")
print("前端: http://192.168.31.105:8866")
