import paramiko
import os

NAS_IP = "192.168.31.105"
NAS_PORT = 22
NAS_USER = "Kirito"
NAS_PASSWORD = "Jia501688921"

def run_command(command, use_sudo=False):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=10)
        
        if use_sudo:
            command = f"sudo -i bash -c '{command}'"
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            stdin.write(f"{NAS_PASSWORD}\n")
            stdin.flush()
        else:
            stdin, stdout, stderr = ssh.exec_command(command)
        
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        return output, error
    finally:
        ssh.close()

def sftp_upload(local_path, remote_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(NAS_IP, port=NAS_PORT, username=NAS_USER, password=NAS_PASSWORD, timeout=10)
        sftp = ssh.open_sftp()
        
        if os.path.isdir(local_path):
            remote_dir = remote_path
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                sftp.mkdir(remote_dir)
            
            for root, dirs, files in os.walk(local_path):
                for dirname in dirs:
                    local_dir = os.path.join(root, dirname)
                    rel_path = os.path.relpath(local_dir, local_path)
                    remote_subdir = os.path.join(remote_dir, rel_path)
                    try:
                        sftp.stat(remote_subdir)
                    except FileNotFoundError:
                        sftp.mkdir(remote_subdir)
                
                for filename in files:
                    local_file = os.path.join(root, filename)
                    rel_path = os.path.relpath(local_file, local_path)
                    remote_file = os.path.join(remote_dir, rel_path)
                    sftp.put(local_file, remote_file)
        else:
            sftp.put(local_path, remote_path)
        
        sftp.close()
        return True, "上传成功"
    except Exception as e:
        return False, str(e)
    finally:
        ssh.close()

def main():
    print("=" * 60)
    print("飞牛NAS 安全整改系统部署")
    print("=" * 60)
    
    print("\n[1/6] 创建目录...")
    cmd = "mkdir -p /vol2/1000/Docker/anquan/backend /vol2/1000/Docker/safety-vue-simple /vol1/1000/工作资料/安全资料/photos && chmod -R 777 /vol2/1000/Docker /vol1/1000/工作资料/安全资料"
    output, error = run_command(cmd, use_sudo=True)
    if "denied" in error.lower():
        print(f"   ❌ 权限错误")
        return
    print("   ✅ 完成")
    
    print("\n[2/6] 上传后端代码...")
    local_backend = "/Users/kirito/Downloads/12/111/backend"
    remote_backend = "/vol2/1000/Docker/anquan/backend"
    success, msg = sftp_upload(local_backend, remote_backend)
    if success:
        print(f"   ✅ {msg}")
    else:
        print(f"   ❌ {msg}")
        return
    
    print("\n[3/6] 上传Vue前端代码...")
    local_vue = "/Users/kirito/Downloads/12/111/safety-vue-simple"
    remote_vue = "/vol2/1000/Docker/safety-vue-simple"
    success, msg = sftp_upload(local_vue, remote_vue)
    if success:
        print(f"   ✅ {msg}")
    else:
        print(f"   ❌ {msg}")
        return
    
    print("\n[4/6] 更新后端服务...")
    commands = [
        "cd /vol2/1000/Docker/anquan/backend && docker compose down 2>/dev/null || true",
        "cd /vol2/1000/Docker/anquan/backend && docker compose up -d --build"
    ]
    for cmd in commands:
        output, error = run_command(cmd, use_sudo=True)
        if "denied" in error.lower():
            print(f"   ❌ 权限错误")
            return
        print(f"   ✅ 执行成功")
    
    print("\n[5/6] 构建并启动Vue前端...")
    commands = [
        "cd /vol2/1000/Docker/safety-vue-simple && npm config set registry https://registry.npmmirror.com",
        "cd /vol2/1000/Docker/safety-vue-simple && npm install --legacy-peer-deps",
        "cd /vol2/1000/Docker/safety-vue-simple && npm run build",
        "cd /vol2/1000/Docker/safety-vue-simple && docker compose down 2>/dev/null || true",
        "cd /vol2/1000/Docker/safety-vue-simple && docker compose up -d"
    ]
    for i, cmd in enumerate(commands, 1):
        print(f"   步骤 {i}/5...")
        output, error = run_command(cmd, use_sudo=True)
        if "denied" in error.lower():
            print(f"   ❌ 权限错误")
            return
        if output:
            print(f"      {output.strip()[:100]}")
        print(f"   ✅ 完成")
    
    print("\n[6/6] 检查服务状态...")
    output, error = run_command("docker ps | grep -E 'safety|vue'", use_sudo=True)
    if output:
        print("   ✅ 服务运行中:")
        print(output)
    else:
        print("   ❌ 服务未运行")
        output, error = run_command("docker ps -a", use_sudo=True)
        print("   所有容器:")
        print(output)
    
    print("\n" + "=" * 60)
    print("🎉 部署完成！")
    print("=" * 60)
    print("\n访问地址:")
    print("  - Vue前端: http://192.168.31.105:8866/")
    print("  - 后端API: http://192.168.31.105:9999")
    print("  - API文档: http://192.168.31.105:9999/docs")

if __name__ == "__main__":
    main()