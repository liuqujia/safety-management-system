import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

print("=== 查看容器内模型定义 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker exec safety-management-api cat /app/app/models.py')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
