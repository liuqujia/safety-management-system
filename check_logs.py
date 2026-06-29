import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

print("=== 查看容器日志 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker logs safety-management-api --tail=20')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
