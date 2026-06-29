import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

sftp = ssh.open_sftp()

print("上传issues.py...")
local_path = '/Users/kirito/Downloads/12/111/backend/app/api/issues.py'
remote_path = '/vol2/1000/Docker/anquan/backend/app/api/issues.py'
sftp.put(local_path, remote_path)

print("上传requirements.txt...")
local_path = '/Users/kirito/Downloads/12/111/backend/requirements.txt'
remote_path = '/vol2/1000/Docker/anquan/backend/requirements.txt'
sftp.put(local_path, remote_path)

sftp.close()

print("重启Docker服务...")
stdin, stdout, stderr = ssh.exec_command('cd /vol2/1000/Docker/anquan/backend && docker compose down && docker compose up -d --build')
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))

ssh.close()
print('后端修改完成！')
