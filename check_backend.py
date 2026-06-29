import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

stdin, stdout, stderr = ssh.exec_command('cd /vol2/1000/Docker/anquan/backend && docker compose ps')
print("=== Docker状态 ===")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command('cd /vol2/1000/Docker/anquan/backend && docker compose logs --tail=20')
print("\n=== 后端日志 ===")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command('grep -n "import-from-word" /vol2/1000/Docker/anquan/backend/app/api/issues.py')
print("\n=== Word导入API位置 ===")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
