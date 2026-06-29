import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

sftp = ssh.open_sftp()

print("上传issues.py...")
local_path = '/Users/kirito/Downloads/12/111/backend/app/api/issues.py'
remote_path = '/vol2/1000/Docker/anquan/backend/app/api/issues.py'
sftp.put(local_path, remote_path)

sftp.close()

print("\n=== 重启后端服务 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker compose -f /vol2/1000/Docker/anquan/backend/docker-compose.yml down')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("\n=== 构建并启动 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker compose -f /vol2/1000/Docker/anquan/backend/docker-compose.yml up -d --build')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("\n=== Docker状态 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker compose -f /vol2/1000/Docker/anquan/backend/docker-compose.yml ps')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
