import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

print("=== 查看export.py第280-300行 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker exec safety-management-api sed -n "280,300p" /app/app/api/export.py')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("\n=== 查看完整的export_to_excel_with_photos函数 ===")
stdin, stdout, stderr = ssh.exec_command('echo Jia501688921 | sudo -S docker exec safety-management-api grep -n "def export_to_excel_with_photos" /app/app/api/export.py')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
