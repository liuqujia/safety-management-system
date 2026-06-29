import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

sftp = ssh.open_sftp()

print("读取export.py...")
with sftp.file('/vol2/1000/Docker/anquan/backend/app/api/export.py', 'r') as f:
    content = f.read().decode('utf-8')

content = content.replace('cell = ws.cell(row=row_num, column=col_num, value=header)', 'cell = ws.cell(row=1, column=col_num, value=header)')

print("写入export.py...")
with sftp.file('/vol2/1000/Docker/anquan/backend/app/api/export.py', 'w') as f:
    f.write(content.encode('utf-8'))

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
print("\n修复完成！")
