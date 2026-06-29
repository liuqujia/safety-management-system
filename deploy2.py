import paramiko
import os

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=10)

print("1/6 创建目录...")
cmd = "sudo -i mkdir -p /vol2/1000/Docker/anquan/backend /vol2/1000/Docker/safety-vue-simple /vol1/1000/工作资料/安全资料/photos && sudo -i chmod -R 777 /vol2/1000/Docker /vol1/1000/工作资料/安全资料"
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
stdin.write(NAS_PASSWORD + "\n")
stdin.flush()
stdout.channel.recv_exit_status()
print("OK")

print("2/6 上传后端代码...")
sftp = ssh.open_sftp()
local = "/Users/kirito/Downloads/12/111/backend"
remote = "/vol2/1000/Docker/anquan/backend"
for root, dirs, files in os.walk(local):
    for d in dirs:
        rd = os.path.join(remote, os.path.relpath(os.path.join(root, d), local))
        try: sftp.stat(rd)
        except: sftp.mkdir(rd)
    for f in files:
        lp = os.path.join(root, f)
        rp = os.path.join(remote, os.path.relpath(lp, local))
        sftp.put(lp, rp)
sftp.close()
print("OK")

print("3/6 上传Vue前端...")
sftp = ssh.open_sftp()
local = "/Users/kirito/Downloads/12/111/safety-vue-simple"
remote = "/vol2/1000/Docker/safety-vue-simple"
for root, dirs, files in os.walk(local):
    for d in dirs:
        rd = os.path.join(remote, os.path.relpath(os.path.join(root, d), local))
        try: sftp.stat(rd)
        except: sftp.mkdir(rd)
    for f in files:
        lp = os.path.join(root, f)
        rp = os.path.join(remote, os.path.relpath(lp, local))
        sftp.put(lp, rp)
sftp.close()
print("OK")

print("4/6 启动后端服务...")
cmd = "cd /vol2/1000/Docker/anquan/backend && sudo docker compose down 2>/dev/null || true && sudo docker compose up -d --build"
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
stdin.write(NAS_PASSWORD + "\n")
stdin.flush()
stdout.channel.recv_exit_status()
print("OK")

print("5/6 构建Vue前端...")
cmds = [
    "cd /vol2/1000/Docker/safety-vue-simple && npm config set registry https://registry.npmmirror.com",
    "cd /vol2/1000/Docker/safety-vue-simple && npm install --legacy-peer-deps",
    "cd /vol2/1000/Docker/safety-vue-simple && npm run build",
    "cd /vol2/1000/Docker/safety-vue-simple && sudo docker compose down 2>/dev/null || true",
    "cd /vol2/1000/Docker/safety-vue-simple && sudo docker compose up -d"
]
for i, cmd in enumerate(cmds):
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    stdin.write(NAS_PASSWORD + "\n")
    stdin.flush()
    stdout.channel.recv_exit_status()
    print(f"  {i+1}/5 OK")

print("6/6 检查服务状态...")
cmd = "sudo docker ps | grep -E 'safety|vue'"
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
stdin.write(NAS_PASSWORD + "\n")
stdin.flush()
output = stdout.read().decode("utf-8")
print("服务状态:\n", output)

ssh.close()
print("\n部署完成!")
print("前端: http://192.168.31.105:8866")
print("后端: http://192.168.31.105:9999")