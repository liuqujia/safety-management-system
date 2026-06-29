import paramiko

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"

print("测试SSH连接...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=5)
    print("✅ 连接成功！")
    
    stdin, stdout, stderr = ssh.exec_command("whoami")
    output = stdout.read().decode('utf-8').strip()
    print(f"当前用户: {output}")
    
    stdin, stdout, stderr = ssh.exec_command("pwd")
    output = stdout.read().decode('utf-8').strip()
    print(f"当前目录: {output}")
    
    stdin, stdout, stderr = ssh.exec_command("docker ps")
    output = stdout.read().decode('utf-8')
    print(f"Docker状态:\n{output}")
    
except Exception as e:
    print(f"❌ 连接失败: {str(e)}")
    
finally:
    ssh.close()
    
print("\n测试完成")