import paramiko

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=10)

print("上传更新的export.py...")
sftp = ssh.open_sftp()
sftp.put("/Users/kirito/Downloads/12/111/backend/app/api/export.py", "/vol2/1000/Docker/anquan/backend/app/api/export.py")
sftp.close()

print("重启后端服务...")
cmd = "cd /vol2/1000/Docker/anquan/backend && sudo docker compose down && sudo docker compose up -d --build"
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
stdin.write(NAS_PASSWORD + "\n")
stdin.flush()
stdout.channel.recv_exit_status()
print("OK")

print("检查服务状态...")
cmd = "sudo docker ps | grep safety-management"
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
stdin.write(NAS_PASSWORD + "\n")
stdin.flush()
output = stdout.read().decode("utf-8")
print("服务状态:", output)

ssh.close()
print("更新完成!")